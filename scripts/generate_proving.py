import os
import sympy
import numpy as np
import json
import random
import time
import signal
import threading
import itertools
from contextlib import contextmanager
from typing import Optional, Dict, Any

from pyeuclid.formalization.relation import *
from pyeuclid.formalization.diagram import Diagram
from pyeuclid.formalization.state import State
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.translation import get_constructions_from_goal
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.inference_rule import *
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

independent_rules = [rule for rule in construction_rule_sets["proving"] if rule in construction_rule_sets["independent"]]
deterministic_rules = [rule for rule in construction_rule_sets["proving"] if rule in construction_rule_sets["deterministic"]]
nondeterministic_rules = [rule for rule in construction_rule_sets["proving"] if rule in construction_rule_sets["nondeterministic"]]


def is_angle_sum_minus_pi(expr: sympy.Expr) -> bool:
    if not isinstance(expr, sympy.Add):
        return False
    terms = list(expr.args)
    if -sympy.pi not in terms:
        return False
    terms.remove(-sympy.pi)
    if len(terms) != 2:
        return False
    a, b = terms
    return isinstance(a, sympy.Symbol) and isinstance(b, sympy.Symbol) and a.name.startswith("Angle_") and b.name.startswith("Angle_")

def is_angle_diff(expr: sympy.Expr) -> bool:
    # Angle_X_Y_Z - Angle_Y_Z_W
    if not isinstance(expr, sympy.Add) or len(expr.args) != 2:
        return False
    a, b = expr.args
    return isinstance(a, sympy.Symbol) and isinstance(b, sympy.Mul) and b.args[0] == -1 and isinstance(b.args[1], sympy.Symbol) and a.name.startswith("Angle_") and b.args[1].name.startswith("Angle_")

def is_length_diff(expr: sympy.Expr) -> bool:
    # Length_A_B - Length_C_D
    if not isinstance(expr, sympy.Add) or len(expr.args) != 2:
        return False
    a, b = expr.args
    return isinstance(a, sympy.Symbol) and isinstance(b, sympy.Mul) and b.args[0] == -1 and isinstance(b.args[1], sympy.Symbol) and a.name.startswith("Length_") and b.args[1].name.startswith("Length_")

def is_length_ratio_diff(expr: sympy.Expr) -> bool:
    # Length/Length - Length/Length
    if not isinstance(expr, sympy.Add) or len(expr.args) != 2:
        return False
    def is_len_ratio(term):
        if not isinstance(term, sympy.Mul) or len(term.args) != 2:
            return False
        a, b = term.args
        return isinstance(a, sympy.Symbol) and a.name.startswith("Length_") and isinstance(b, sympy.Pow) and b.exp == -1 and isinstance(b.base, sympy.Symbol) and b.base.name.startswith("Length_")
    a, b = expr.args
    return is_len_ratio(a) and b.could_extract_minus_sign() and is_len_ratio(-b)


class TimeoutHandler:
    def __init__(self, timeout_seconds: Optional[int] = None):
        self.timeout_occurred = False
        self.timeout_seconds = timeout_seconds
        self.start_time = time.time()
        self.lock = threading.Lock()

    def timeout_handler(self, signum, frame):
        """Handles SIGTERM for graceful timeout"""
        with self.lock:
            self.timeout_occurred = True
        print(f"Timeout signal received (signal {signum})")

    def check_timeout(self) -> bool:
        """Check if timeout has occurred or time limit exceeded"""
        with self.lock:
            if self.timeout_occurred:
                return True

        if self.timeout_seconds:
            elapsed = time.time() - self.start_time
            if elapsed >= self.timeout_seconds:
                with self.lock:
                    self.timeout_occurred = True
                print(f"Time limit exceeded: {elapsed:.2f}s >= {self.timeout_seconds}s")
                return True

        return False

    def get_elapsed_time(self) -> float:
        return time.time() - self.start_time

    def get_remaining_time(self) -> Optional[float]:
        if not self.timeout_seconds:
            return None
        return max(0, self.timeout_seconds - self.get_elapsed_time())

@contextmanager
def timeout_context(timeout_seconds: Optional[int] = None):
    """Context manager that handles SIGTERM for graceful shutdown and SIGINT for immediate exit"""
    timeout_handler = TimeoutHandler(timeout_seconds)

    # Set up signal handlers
    old_sigterm = signal.signal(signal.SIGTERM, timeout_handler.timeout_handler)

    def handle_sigint(signum, frame):
        print("SIGINT (Ctrl+C) received — exiting immediately")
        raise KeyboardInterrupt()

    old_sigint = signal.signal(signal.SIGINT, handle_sigint)

    try:
        yield timeout_handler
    finally:
        # Restore original signal handlers
        signal.signal(signal.SIGTERM, old_sigterm)
        signal.signal(signal.SIGINT, old_sigint)

def generate_single_problem(rank: int, output_dir: str, problem_id: int,
                            timeout_handler: TimeoutHandler,
                            seed_offset: int = 0) -> Dict[str, Any]:
    """Generate a single problem with timeout checking at key points.

    `seed_offset` lets us retry the same problem_id with a different seed.
    """
    if timeout_handler.check_timeout():
        return {"samples_generated": 0, "samples_with_auxiliary": 0, "timeout": True}

    problem_output_dir = os.path.join(output_dir, f'rank_{rank}', f'problem_{problem_id}')
    os.makedirs(problem_output_dir, exist_ok=True)

    # Make retries non-deterministic w.r.t. the same problem_id
    base_seed = 42 + rank * 1000 + problem_id + 100000 * seed_offset
    hash_seed = os.environ.get("PYTHONHASHSEED", 0)
    random.seed(base_seed)
    np.random.seed(base_seed)
    sympy.core.random.seed(base_seed)

    state = State()
    state.silent = True
    deductive_database = DeductiveDatabase(state)
    algebraic_system = AlgebraicSystem(state)
    engine = Engine(state, deductive_database, algebraic_system)
    point2constructions = {}

    diagram_path = os.path.join(problem_output_dir, f'diagram_rank_{rank}_problem_{problem_id}.jpg')
    diagram = Diagram(cache_folder=None, save_path=diagram_path)
    state.diagram = diagram

    step = 0
    attempt = 0
    points = 0

    max_steps = random.uniform(3, 5)
    max_attempts = 100
    max_points = 8
    constructions_list = []
    index = 0
    # Construction phase with timeout checks
    while (step < max_steps and attempt < max_attempts and points < max_points
           and not timeout_handler.check_timeout()):

        constructions = []
        multiconstructions = False

        if step == 0:
            candidate_set = independent_rules
        else:
            rand = random.random()
            if rand < 0.2:
                candidate_set = [rule for rule in deterministic_rules
                                 if rule.num_inputs <= len(state.points)]
            else:
                rand = random.random()
                multiconstructions = False if rand < 0.2 else True
                candidate_set = [rule for rule in nondeterministic_rules
                                 if rule.num_inputs <= len(state.points)]

        picked = random.choice(candidate_set)
        all_points = list(state.points.copy())
        num_points = len(all_points)

        valid_constructions = []

        # Generate candidate input combinations
        assert all(typ == Point for typ in picked.input_types)
        # For input types that are all points
        candidates = itertools.permutations(all_points, len(picked.input_types))
        for candidate in candidates:
            construction = picked(*candidate)
            conditions = construction.conditions()
            if all(diagram.numerical_check(cond) for cond in conditions):
                valid_constructions.append(construction)
        
        if not valid_constructions:
            attempt += 1
            continue

        construction = random.choice(valid_constructions)
        outputs = [Point(chr(ord('a') + num_points + i)) for i in range(picked.num_outputs)]
        construction.construct(*outputs)
        constructions.append(construction)

        if multiconstructions:
            candidate_set = [rule for rule in nondeterministic_rules
                             if rule.num_inputs <= len(state.points) and
                             rule.num_outputs == picked.num_outputs]
            picked = random.choice(candidate_set)
            all_points = list(state.points.copy())
            num_points = len(all_points)

            valid_constructions = []

            assert all(typ == Point for typ in picked.input_types)
            candidates = itertools.product(all_points, repeat=len(picked.input_types))
            for candidate in candidates:
                construction = picked(*candidate)
                conditions = construction.conditions()
                if all(diagram.numerical_check(cond) for cond in conditions):
                    valid_constructions.append(construction)

            if not valid_constructions:
                attempt += 1
                continue

            if constructions[0] in valid_constructions:
                valid_constructions.remove(constructions[0])

            construction = random.choice(valid_constructions)
            construction.construct(*outputs)
            constructions.append(construction)

        attempt += 1
        try:
            diagram.add_constructions(constructions)
        except:
            continue

        constructions_list.append(constructions)
        for construction in constructions:
            construction.index = index
            index += 1
        
        state.add_constructions(constructions)
        step += 1
        points += len(outputs)
        for p in outputs:
            point2constructions[p] = constructions
    
    with open(os.path.join(problem_output_dir, f'constructions_list.json'), 'w') as f:
        s = ', '.join([str(construction) for constructions in constructions_list for construction in constructions])
        f.write(s)
    
    print('running engine')
    
    try:
        engine.run()
    except:
        print('engine error!')
        return {"samples_generated": 0}
    
    print('finish engine')

    conclusions = list(state.relations) + list(state.equations)
        
    if timeout_handler.check_timeout():
        return {"samples_generated": 0, "timeout": True}

    max_depth = max(state.condition2depth.values())

    if max_depth <= 2:
        print(f'depth to low: {max_depth}')
        return {"samples_generated": 0}

    conclusions = [c for c in conclusions if state.condition2depth.get(c) > 2 and state.condition2depth.get(c) >= max_depth - 1]
    # filter conclusions
    filtered_conclusions = []
    for relation in conclusions:
        if isinstance(relation, Relation) and not isinstance(relation, (Concyclic, Collinear, Perpendicular, Parallel, Midpoint, Similar3, Congruent3)):
            continue
        # degenerated cases
        elif isinstance(relation, Congruent3):
            points = relation.get_points()
            if len(set(points)) == 3:
                continue
        elif isinstance(relation, Similar3):
            points = relation.get_points()
            if len(set(points)) == 3:
                continue
            if Congruent3(*points) in state.relations:
                continue
        elif isinstance(relation, Parallel):
            points = relation.get_points()
            if len(set(points)) == 3:
                continue
            elif diagram.numerical_check(Collinear(*points[:3])):
                continue
        elif isinstance(relation, Traced):
            # length_a - length_b, length_a/length_b - length_c/length_d, angle_a - angle_b, angle_a + angle_b - pi
            expr = relation.expr
            if not is_angle_diff(expr) and not is_angle_sum_minus_pi(expr) and not is_length_diff(expr) and not is_length_ratio_diff(expr):
                continue
        filtered_conclusions.append(relation)
    
    if not filtered_conclusions:
        return {"samples_generated": 0}

    relations = [c for c in filtered_conclusions if isinstance(c, Relation)]
    random.shuffle(relations)
    angle_diffs = [c for c in filtered_conclusions if isinstance(c, Traced) and is_angle_diff(c.expr)]
    random.shuffle(angle_diffs)
    angle_sums = [c for c in filtered_conclusions if isinstance(c, Traced) and is_angle_sum_minus_pi(c.expr)]
    random.shuffle(angle_sums)
    length_diffs = [c for c in filtered_conclusions if isinstance(c, Traced) and is_length_diff(c.expr)]
    random.shuffle(length_diffs)
    ratio_diffs = [c for c in filtered_conclusions if isinstance(c, Traced) and is_length_ratio_diff(c.expr)]
    random.shuffle(ratio_diffs)

    traced_groups = [angle_diffs, angle_sums, length_diffs, ratio_diffs]
    random.shuffle(traced_groups)
    traced = sum(traced_groups, [])

    if random.random() < 0.5:
        filtered_conclusions = relations + traced
    else:
       filtered_conclusions = traced + relations

    proof_generator = ProofGenerator(state, max_equation_length_perstep=None)

    def get_sufficient_constructions(points):
        res = []
        target_points = set(points)
        seen_points = set()
        def mark_sufficient(point):
            if point in seen_points:
                return
            seen_points.add(point)
            for c in point2constructions[point]:
                if c not in res:
                    res.append(c)
                    for inp in c.inputs:
                        mark_sufficient(inp)
        for point in target_points:
            mark_sufficient(point)
        return sorted(res, key=lambda c: c.index)
    
    samples_generated = False

    for relation in filtered_conclusions:
        if timeout_handler.check_timeout():
            break
        if isinstance(relation, Traced):
            key = relation.expr
        else:
            key = relation

        if isinstance(relation, Relation):
            points = relation.get_points()
        else:
            points_list = get_points_and_symbols(relation)[0]
            points = [p for points in points_list for p in points]

        sufficient_constructions = get_sufficient_constructions(points)
        sufficient_constructions = sorted(sufficient_constructions, key=lambda c: c.index)
        new_state = State()
        new_state.silent = True
        new_state.goal = relation.expr if isinstance(relation, Traced) else relation
        new_state.diagram = diagram
        new_state.add_constructions(sufficient_constructions)
        new_deductive_database = DeductiveDatabase(new_state)
        new_algebraic_system = AlgebraicSystem(new_state)
        new_engine = Engine(new_state, new_deductive_database, new_algebraic_system)
        try:
            new_engine.run()
        except:
            print('new_engine error!')
            continue

        if new_state.complete() is None:
            print('new_engine cannot solve')
            continue

        if new_state.condition2depth[key] <= 2:
            print('depth too easy')
            continue

        new_proof_generator = ProofGenerator(new_state, max_equation_length_perstep=None, norm=0)
        try:
            new_proof_generator.run()
            new_proof = new_proof_generator.get_proof()
        except:
            print('new_proof wrong!!')
            input()
        
        if len(new_proof) <= 4:
            print('proof too easy')
            continue

        new_proof_str = new_proof_generator.get_proof_str(angle='degree')

        necessary_constructions = new_proof_generator.source_constructions[key]

        if len(necessary_constructions) <= 2:
            print('neccessy constructions too easy')
            continue

        input_points  = {p for c in necessary_constructions for p in c.inputs  if isinstance(p, Point)}
        output_points = {p for c in necessary_constructions for p in c.outputs if isinstance(p, Point)}
        if not input_points.issubset(output_points):
            continue

        sample_dir = os.path.join(problem_output_dir, f'sample_0')
        os.makedirs(sample_dir, exist_ok=True)

        diagram_sample_path = os.path.join(sample_dir, 'diagram.jpg')
        diagram.save_path = diagram_sample_path

        goal_constructions = get_constructions_from_goal(relation)
        diagram.draw([], goal_constructions)
        diagram.draw_diagram(constructions=necessary_constructions+goal_constructions, save=True)        
        diagram.restore()

        problem_constructions = sorted(necessary_constructions, key=lambda c: c.index)
        coordinates = []
        for name, point in diagram.name2point.items():
            coordinates.append(f"{name}: ({str(point.x)}, {str(point.y)})")

        data = {
            "problem": ', '.join([str(construction) for construction in problem_constructions]),
            "goal": str(relation),
            "diagram": diagram_sample_path,
            "proof": new_proof_str,
            "coordinates": ', '.join(coordinates),
            "depth": new_state.condition2depth[key],
            "seed": base_seed,
        }

        with open(os.path.join(sample_dir, "data.json"), "w") as f:
            json.dump(data, f, indent=4)
        
        samples_generated = True
        print('Generated 1 sample...')
        break

    return {
        "samples_generated": 1 if samples_generated else 0,
        "timeout": timeout_handler.check_timeout()
    }

def generate_until_timeout(rank: int, output_dir: str, timeout_handler: TimeoutHandler,
                           max_problem_id: Optional[int] = None) -> Dict[str, Any]:
    """Generate problems until timeout with improved progress tracking.

    Only advance problem_id when a problem yields at least one sample.
    """
    rank_output_dir = os.path.join(output_dir, f'rank_{rank}')
    os.makedirs(rank_output_dir, exist_ok=True)

    problem_id = 0
    total_samples = 0
    start_time = time.time()
    problems_with_errors = 0
    problems_with_timeouts = 0

    # Track retries for the current problem_id; influences RNG seed
    retries_for_problem_id = 0
    try:
        while not timeout_handler.check_timeout():
            if max_problem_id and problem_id >= max_problem_id:
                break

            result = generate_single_problem(
                rank, output_dir, problem_id, timeout_handler,
                seed_offset=retries_for_problem_id
            )

            if result.get("timeout"):
                problems_with_timeouts += 1
                break

            if result.get("error"):
                problems_with_errors += 1

            total_samples += result["samples_generated"]

            if result["samples_generated"] > 0:
                problem_id += 1
                retries_for_problem_id = 0
            else:
                retries_for_problem_id += 1

    except Exception as e:
        print(f"Rank {rank}: Fatal error in generation loop: {e}")
        raise

    duration = timeout_handler.get_elapsed_time()

    # Determine termination reason
    if timeout_handler.check_timeout():
        termination_reason = "timeout_during_problem" if problems_with_timeouts > 0 else "timeout"
    elif max_problem_id and problem_id >= max_problem_id:
        termination_reason = "max_problems_reached"
    else:
        termination_reason = "completed"

    result = {
        "total_samples": total_samples,
        "total_problems": problem_id,
        "problems_with_errors": problems_with_errors,
        "problems_with_timeouts": problems_with_timeouts,
        "termination_reason": termination_reason,
        "duration": duration,
        "problems_per_second": problem_id / duration if duration > 0 else 0,
        "samples_per_second": total_samples / duration if duration > 0 else 0
    }
    return result

def main():
    rank = int(os.environ.get("SLURM_ARRAY_TASK_ID", "0"))
    timeout_seconds = int(os.environ.get("TIMEOUT_SECONDS", "3600"))
    max_problem_id = int(os.environ.get("MAX_PROBLEM_ID", "100"))
    base_output_dir = os.environ.get('OUTPUT_DIR', 'dataset')

    os.makedirs(base_output_dir, exist_ok=True)

    with timeout_context(timeout_seconds if timeout_seconds > 0 else None) as timeout_handler:
        result = generate_until_timeout(
            rank, base_output_dir, timeout_handler,
            max_problem_id=max_problem_id if max_problem_id > 0 else None
        )

if __name__ == '__main__':
    main()