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

independent_rules = [rule for rule in construction_rule_sets["auxiliary_construction"] if rule in construction_rule_sets["independent"]]
deterministic_rules = [rule for rule in construction_rule_sets["auxiliary_construction"] if rule in construction_rule_sets["deterministic"]]
nondeterministic_rules = [rule for rule in construction_rule_sets["auxiliary_construction"] if rule in construction_rule_sets["nondeterministic"]]

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
    random.seed(base_seed)
    np.random.seed(base_seed)

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

    max_steps = random.uniform(6, 12)
    max_attempts = 100
    max_points = random.uniform(10, 20)
    constructions_list = []
    index = 0
    old_relations = []
    old_equations = []
    conclusions = []

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

        engine.run()
        for relation in state.relations:
            if relation not in old_relations:
                ps = set(relation.get_points())
                if all([p not in outputs for p in ps]) and not trivial_condition(relation) and hasattr(relation, "source"):
                    conclusions.append(relation)
                old_relations.append(relation)
        for equation in state.equations:
            if equation not in old_equations:
                ps = set([p for points in get_points_and_symbols(equation)[0] for p in points])
                if all([p not in outputs for p in ps]) and equation.sources and isinstance(equation.sources[0], InferenceRule) and not isinstance(equation.sources[0], (DiagramAngle4a, DiagramAngle4b, DiagramAngle2, FlatAngle, FlatAngle2)):
                    conclusions.append(equation)
                old_equations.append(equation)
        
    if timeout_handler.check_timeout():
        return {"samples_generated": 0, "samples_with_auxiliary": 0, "timeout": True}

    i = 0
    samples_with_auxiliary = 0
    sub_conclusions = set()
    conclusions2dir = {}

    proof_generator = ProofGenerator(state, max_equation_length_perstep=None)
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
        return {"samples_generated": 0, "samples_with_auxiliary": 0}

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

        proof_generator.run(relation)
        auxiliary_constructions = sorted([c for c in proof_generator.source_constructions[key] if c not in sufficient_constructions], key=lambda c: c.index)
        sufficient_auxiliary_constructions = []
        for auxiliary_construction in auxiliary_constructions:
            sufficient_auxiliary_constructions.append(auxiliary_construction)
            for construction in get_sufficient_constructions([p for p in auxiliary_construction.inputs if isinstance(p, Point)]):
                if construction not in sufficient_constructions and construction not in sufficient_auxiliary_constructions:
                    sufficient_auxiliary_constructions.append(construction)
        sufficient_auxiliary_constructions = sorted(sufficient_auxiliary_constructions, key=lambda c: c.index)
        auxiliary_constructions = sufficient_auxiliary_constructions.copy()

        for auxiliary_construction in sufficient_auxiliary_constructions[::-1]:
            new_auxiliary_constructions = auxiliary_constructions.copy()
            new_auxiliary_constructions.remove(auxiliary_construction)
            new_constructions = sufficient_constructions + new_auxiliary_constructions
            new_state = State()
            new_state.silent = True
            new_state.goal = relation.expr if isinstance(relation, Traced) else relation
            new_state.diagram = diagram
            new_state.add_constructions(new_constructions)
            new_deductive_database = DeductiveDatabase(new_state)
            new_algebraic_system = AlgebraicSystem(new_state)
            new_engine = Engine(new_state, new_deductive_database, new_algebraic_system)
            new_engine.run()
            if new_state.complete() is not None:
                # the auxiliary construction is not required
                auxiliary_constructions.remove(auxiliary_construction)

        new_state = State()
        new_state.silent = True
        new_state.goal = relation.expr if isinstance(relation, Traced) else relation
        new_state.diagram = diagram
        new_state.add_constructions(sorted(sufficient_constructions+auxiliary_constructions, key=lambda c: c.index))
        new_deductive_database = DeductiveDatabase(new_state)
        new_algebraic_system = AlgebraicSystem(new_state)
        new_engine = Engine(new_state, new_deductive_database, new_algebraic_system)
        new_engine.run()
        assert new_state.complete() is not None

        if new_state.condition2depth[key] <= 2:
            continue

        new_proof_generator = ProofGenerator(new_state, max_equation_length_perstep=None)
        new_proof_generator.run()
        new_proof = new_proof_generator.get_proof()
        new_proof_str = new_proof_generator.get_proof_str()

        necessary_constructions = [construction for construction in sufficient_constructions if construction in new_proof_generator.source_constructions[key]]

        if len(necessary_constructions) <= 2:
            continue

        input_points = set()
        output_points = set()
        for construction in new_proof_generator.source_constructions[key]:
            input_points.update([p for p in construction.inputs if isinstance(p, Point)])
            output_points.update([p for p in construction.outputs])

        added_constructions = []
        basic_points = []
        for p in sorted(list(input_points), key=lambda p:p.name):
            if p not in output_points:
                if len(point2constructions[p]) == 1 and type(point2constructions[p][0]) in list(construction_rule_sets["independent"]):
                    basic_points.append(p)
                else:
                    c = construct_free()
                    c.construct(p)
                    c.index = point2constructions[p][0].index
                    added_constructions.append(c)

        if len(basic_points) == 1:
            c = construct_free()
            c.construct(*basic_points)
            c.index = 0
            added_constructions.append(c)
        elif len(basic_points) == 2:
            c = construct_segment()
            c.construct(*basic_points)
            c.index = 0
            added_constructions.append(c)
        elif len(basic_points) == 3:
            c = construct_triangle()
            c.construct(*basic_points)
            c.index = 0
            added_constructions.append(c)
        elif len(basic_points) == 4:
            c = construct_quadrangle()
            c.construct(*basic_points)
            c.index = 0
            added_constructions.append(c)
        elif len(basic_points) == 5:
            c = construct_pentagon()
            c.construct(*basic_points)
            c.index = 0
            added_constructions.append(c)

        for (conditions, _, _) in new_proof:
            for cond in conditions:
                if isinstance(cond, sympy.core.expr.Expr):
                    cond = Traced(cond)
                if cond in conclusions:
                    sub_conclusions.add(cond)

        has_auxiliary = len(auxiliary_constructions) > 0
        if has_auxiliary:
            aux_proof = 'Auxilirary Construction:\n' if len(auxiliary_constructions) == 1 else 'Auxilirary Constructions:\n'
            for construction in auxiliary_constructions:
                aux_proof = aux_proof + str(construction) + '\n'
            new_proof_str = aux_proof + new_proof_str
            samples_with_auxiliary += 1
        else:
            continue

        diagram.save()
        sample_dir = os.path.join(problem_output_dir, f'sample_{i}')
        os.makedirs(sample_dir, exist_ok=True)

        diagram_sample_path = os.path.join(sample_dir, 'diagram.jpg')
        diagram.save_path = diagram_sample_path

        goal_constructions = get_constructions_from_goal(relation)
        diagram.draw([], goal_constructions)
        diagram.draw_diagram(constructions=necessary_constructions+goal_constructions, save=True)

        new_diagram_sample_path = os.path.join(sample_dir, 'diagram_with_auxiliary_constructions.jpg')
        diagram.save_path = new_diagram_sample_path
        diagram.auxiliary_constructions.extend(auxiliary_constructions)
        diagram.draw_diagram(constructions=necessary_constructions+auxiliary_constructions+goal_constructions, save=True)
        
        diagram.restore()

        problem_constructions = sorted(necessary_constructions+added_constructions, key=lambda c: c.index)

        data = {
            "problem": ', '.join([str(construction) for construction in problem_constructions]),
            "goal": str(relation),
            "diagram": diagram_sample_path,
            "diagram_with_auxiliary_constructions": new_diagram_sample_path,
            "auxiliary_constructions": ', '.join([str(construction) for construction in auxiliary_constructions]),
            "num_auxiliary_constructions": len(auxiliary_constructions),
            "proof": new_proof_str,
        }

        with open(os.path.join(sample_dir, "data.json"), "w") as f:
            json.dump(data, f, indent=4)

        conclusions2dir[relation] = sample_dir
        i += 1

    for relation, sample_dir in conclusions2dir.items():
        if os.path.exists(os.path.join(sample_dir, "data.json")):
            with open(os.path.join(sample_dir, "data.json"), "r") as f:
                data = json.load(f)
            data["sub_conclusion"] = True if relation in sub_conclusions else False
            with open(os.path.join(sample_dir, "data.json"), "w") as f:
                json.dump(data, f, indent=4)

    return {
        "samples_generated": i,
        "samples_with_auxiliary": samples_with_auxiliary,
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
    total_samples_with_auxiliary = 0
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
            total_samples_with_auxiliary += result["samples_with_auxiliary"]

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
        "samples_with_auxiliary": total_samples_with_auxiliary,
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
    max_problem_id = int(os.environ.get("MAX_PROBLEM_ID", "0"))
    base_output_dir = os.environ.get('OUTPUT_DIR', 'dataset')

    os.makedirs(base_output_dir, exist_ok=True)

    with timeout_context(timeout_seconds if timeout_seconds > 0 else None) as timeout_handler:
        result = generate_until_timeout(
            rank, base_output_dir, timeout_handler,
            max_problem_id=max_problem_id if max_problem_id > 0 else None
        )

if __name__ == '__main__':
    main()