import os
import sympy
import numpy as np
import json
import random
import time
import signal
import threading
import itertools
import argparse
from contextlib import contextmanager
from typing import Optional, Dict, Any

from euclidea.formalization.relation import *
from euclidea.formalization.diagram import Diagram
from euclidea.formalization.state import State
from euclidea.formalization.construction_rule import *
from euclidea.formalization.translation import get_constructions_from_goal
from euclidea.engine.deductive_database import DeductiveDatabase
from euclidea.engine.inference_rule import *
from euclidea.engine.algebraic_system import AlgebraicSystem
from euclidea.engine.proof_generator import ProofGenerator
from euclidea.engine.engine import Engine

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
        print("SIGINT (Ctrl+C) received 鈥� exiting immediately")
        raise KeyboardInterrupt()

    old_sigint = signal.signal(signal.SIGINT, handle_sigint)

    try:
        yield timeout_handler
    finally:
        # Restore original signal handlers
        signal.signal(signal.SIGTERM, old_sigterm)
        signal.signal(signal.SIGINT, old_sigint)

def generate_single_problem(output_dir: str, problem_id: int,
                            timeout_handler: TimeoutHandler,
                            ) -> Dict[str, Any]:
    problem_output_dir = os.path.join(output_dir, f'problem_{problem_id}')
    os.makedirs(problem_output_dir, exist_ok=True)

    seed = random.randint(0, int(1e9))
    hash_seed = os.environ.get("PYTHONHASHSEED")
    assert hash_seed is not None, (
        "For full reproducibility, please set the environment variable "
        "`PYTHONHASHSEED`, e.g. `export PYTHONHASHSEED=0`."
    )
    random.seed(seed)
    np.random.seed(seed)
    sympy.core.random.seed(seed)

    state = State()
    state.silent = False
    deductive_database = DeductiveDatabase(state)
    algebraic_system = AlgebraicSystem(state)
    engine = Engine(state, deductive_database, algebraic_system)
    point2constructions = {}

    diagram_path = os.path.join(problem_output_dir, f'full_diagram.png')
    diagram = Diagram(cache_folder=None, save_path=diagram_path)
    state.diagram = diagram

    step = 0
    attempt = 0
    points = 0

    max_steps = random.uniform(8, 10)
    max_points = random.uniform(10, 16)
    max_attempts = 100
    
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

        # "problem": "a,b = construct_segment(), c = construct_lc_tangent(a,b), d = construct_on_bline(c,a), d = construct_angle_bisector(c,b,a)",
        # "goal": "Perpendicular(b,d,c,d)",
        # "auxiliary_constructions": "e = construct_intersection_ll(b,a,c,d)",
        
        # if step == 0:
        #     construction = construct_segment()
        #     outputs = [Point('a'), Point('b')]
        #     construction.construct(*outputs)
        #     constructions = [construction]
        # elif step == 1:
        #     construction = construct_lc_tangent(Point('a'), Point('b'))
        #     outputs = [Point('c')]
        #     construction.construct(*outputs)
        #     constructions = [construction]
        # elif step == 2:
        #     construction1 = construct_on_bline(Point('c'), Point('a'))
        #     outputs = [Point('d')]
        #     construction1.construct(*outputs)
        #     construction2 = construct_angle_bisector(Point('c'), Point('b'), Point('a'))
        #     construction2.construct(*outputs)
        #     constructions = [construction1, construction2]
        # elif step == 3:
        #     construction = construct_intersection_ll(Point('b'), Point('a'), Point('c'), Point('d'))
        #     outputs = [Point('e')]
        #     construction.construct(*outputs)
        #     constructions = [construction]
        # else:
        #     break

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

        engine.search()
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
        return 0

    i = 0
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
        return 0
    
    final_conclusions = []

    relations = [c for c in filtered_conclusions if isinstance(c, Relation)]
    if relations:
        final_conclusions.append(random.choice(relations))
    angle_diffs = [c for c in filtered_conclusions if isinstance(c, Traced) and is_angle_diff(c.expr)]
    if angle_diffs:
        final_conclusions.append(random.choice(angle_diffs))
    angle_sums = [c for c in filtered_conclusions if isinstance(c, Traced) and is_angle_sum_minus_pi(c.expr)]
    if angle_sums:
        final_conclusions.append(random.choice(angle_sums))
    length_diffs = [c for c in filtered_conclusions if isinstance(c, Traced) and is_length_diff(c.expr)]
    if length_diffs:
        final_conclusions.append(random.choice(length_diffs))
    ratio_diffs = [c for c in filtered_conclusions if isinstance(c, Traced) and is_length_ratio_diff(c.expr)]
    if ratio_diffs:
        final_conclusions.append(random.choice(ratio_diffs))

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

    for relation in final_conclusions:
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
        try:
            proof_generator.run(relation)
        except:
            continue
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
            try:
                new_engine.search()
            except:
                continue
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
        try:
            new_engine.search()
            assert new_state.complete() is not None
        except:
            continue
        
        new_proof_generator = ProofGenerator(new_state, max_equation_length_perstep=None)
        try:
            new_proof_generator.run()
        except:
            continue
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

        has_auxiliary = len(auxiliary_constructions) > 0
        if has_auxiliary:
            aux_proof = 'Auxilirary Constructions:\n'
            for construction in auxiliary_constructions:
                aux_proof = aux_proof + str(construction) + '\n'
            new_proof_str = aux_proof + new_proof_str
        else:
            continue

        diagram.save()
        sample_dir = os.path.join(output_dir, f'problem_{problem_id+i}')
        os.makedirs(sample_dir, exist_ok=True)

        diagram_sample_path = os.path.join(sample_dir, 'diagram.png')
        diagram.save_path = diagram_sample_path

        goal_constructions = get_constructions_from_goal(relation)
        diagram.draw([], goal_constructions)
        diagram.draw_diagram(constructions=necessary_constructions+goal_constructions, save=True)

        new_diagram_sample_path = os.path.join(sample_dir, 'diagram_with_auxiliary_constructions.png')
        diagram.save_path = new_diagram_sample_path
        diagram.auxiliary_constructions.extend(auxiliary_constructions)
        diagram.draw_diagram(constructions=necessary_constructions+auxiliary_constructions+goal_constructions, save=True)
        
        diagram.restore()

        problem_constructions = sorted(necessary_constructions+added_constructions, key=lambda c: c.index)

        data = {
            "problem_id": problem_id,
            "seed": seed,
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

        i += 1

    return i


def generate_until_timeout(output_dir: str, timeout_handler: TimeoutHandler,
                           max_problem: Optional[int] = None) -> Dict[str, Any]:
    problem_id = 1
    
    while not timeout_handler.check_timeout():
        if max_problem and problem_id >= max_problem:
            break

        generated = generate_single_problem(
            output_dir, problem_id, timeout_handler,
        )

        problem_id += generated


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=3600,
        help="Maximum time (in seconds) to run generation before stopping. Use <=0 for no timeout.",
    )
    parser.add_argument(
        "--max-problem",
        type=int,
        default=0,
        help="Maximum number of problems to generate. Use <=0 for unlimited.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="dataset/auxiliary_constructions",
        help="Directory to store generated problems.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    timeout_seconds = args.timeout_seconds
    max_problem = args.max_problem if args.max_problem > 0 else None
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    with timeout_context(timeout_seconds if timeout_seconds > 0 else None) as timeout_handler:
        generate_until_timeout(
            output_dir,
            timeout_handler,
            max_problem=max_problem,
        )


if __name__ == "__main__":
    main()