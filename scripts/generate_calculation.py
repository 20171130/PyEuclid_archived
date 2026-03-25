import os
import sympy
import numpy as np
import json
import random
import time
import argparse

from stopit import ThreadingTimeout

from euclidea.formalization.relation import *
from euclidea.formalization.diagram import Diagram, MaxAttemptsError
from euclidea.formalization.state import State
from euclidea.formalization.construction_rule import *
from euclidea.formalization.translation import get_constructions_from_goal
from euclidea.formalization.naming_policy import NamePolicy
from euclidea.formalization.utils import expr_complexity
from euclidea.engine.deductive_database import DeductiveDatabase
from euclidea.engine.inference_rule import *
from euclidea.engine.algebraic_system import AlgebraicSystem
from euclidea.engine.proof_generator import ProofGenerator
from euclidea.engine.engine import Engine
from euclidea.formalization.construction_q import ConstructionQ, construct_segment_q, construct_square_q, construct_rectangle_q, construct_angle_counterclockwise, construct_angle_clockwise, construct_point_on_circle, construct_point_on_line, construct_parallelogram_q, construct_eq_trapezoid_q, construct_r_triangle_q, construct_eq_triangle_q, construct_ieq_triangle_q, construct_r_trapezoid_q


def generate_single_problem(output_dir: str, problem_id: int):
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
    state.silent = True
    point2constructions = {}

    diagram_path = os.path.join(problem_output_dir, f'full_diagram.png')
    diagram = Diagram(cache_folder=None, save_path=diagram_path)
    state.diagram = diagram

    step = 0
    attempt = 0
    points = 0
    t0 = time.time()
    
    max_steps = random.uniform(3, 5)
    max_points = random.uniform(8, 10)
    max_attempts = 100

    rule_set = inference_rule_sets["basic"] + inference_rule_sets['complex']
    if random.random() < 0.9:
        rule_set = [item for item in rule_set if not item in (LawOfSines, LawOfCosines, AreaHeronFormula)]
    name_policy = NamePolicy(seed=seed)
    constructions_list = []
    length_values, angle_values = set(), set()
    index = 0
        
    construction_rule_set = [construct_segment_q, construct_r_triangle_q, construct_eq_triangle_q, construct_ieq_triangle_q, construct_r_trapezoid_q, construct_eq_trapezoid_q, construct_square_q, construct_rectangle_q, construct_parallelogram_q]
    construction_rule_set += [construct_angle_counterclockwise, construct_angle_clockwise, construct_point_on_circle, construct_point_on_line, construct_on_dia, construct_angle_bisector, construct_circumcenter, construct_eqdistance, construct_incenter, construct_intersection_cc, construct_intersection_lc, construct_intersection_ll, construct_intersection_lp, construct_intersection_lt, construct_intersection_pp, construct_intersection_tt, construct_lc_tangent, construct_midpoint, construct_mirror, construct_on_aline, construct_on_bline, construct_on_circle, construct_on_line, construct_on_pline, construct_on_tline, construct_orthocenter, construct_reflect]
    construction_rule_set += [construct_foot] * 10

    while (step < max_steps and attempt < max_attempts and len(state.points)<max_points):
        constructions = []
        multiconstructions = False

        if step == 0:
            candidate_set = [rule for rule in construction_rule_set if rule in construction_rule_sets["independent"]]
        else:
            rand = random.random()
            if rand < 0.2:
                candidate_set = [rule for rule in construction_rule_set if rule.num_inputs <= len(state.points) and rule in construction_rule_sets['deterministic']]
            else:
                multiconstructions = True
                candidate_set = [rule for rule in construction_rule_set if rule.num_inputs <= len(state.points) and rule in construction_rule_sets['nondeterministic']]
            
        # remove construct_s_angle if mixing q and non-q construction rules
        picked = random.choice(candidate_set)
        all_points = list(state.points.copy())
        num_points = len(all_points)
        valid_constructions = []

        # Generate candidate input combinations
        if all(typ == Point for typ in picked.input_types):
            # For input types that are all points
            candidates = itertools.permutations(all_points, len(picked.input_types))
            for candidate in candidates:
                if issubclass(picked, ConstructionQ):
                    construction = picked(*candidate, diagram=diagram)
                else:
                    construction = picked(*candidate)
                for condition in construction.conditions():
                    if not diagram.numerical_check(condition):
                        break
                else:
                    valid_constructions.append(construction)

        if not valid_constructions:
            attempt += 1
            continue

        construction = random.choice(valid_constructions)
        used = {p.name for p in state.points}
        labels = name_policy.alloc_labels(picked, picked.num_outputs, used)
        outputs = [Point(lbl) for lbl in labels]
        # outputs = [Point(chr(ord('A') + num_points + i)) for i in range(picked.num_outputs)]
        results = construction.construct(*outputs)
        if not results is None:
            a, b = results
            length_values = length_values.union(a)
            angle_values = angle_values.union(b)
        constructions.append(construction)

        if multiconstructions:
            to_intersect = picked
            candidate_set = [rule for rule in construction_rule_set if rule.num_inputs <= len(state.points) and rule.num_outputs == picked.num_outputs and rule in construction_rule_sets['nondeterministic']]
            rand = random.random()
            picked = random.choice(candidate_set)
            all_points = list(state.points.copy())
            num_points = len(all_points)

            valid_constructions = []

            # Generate candidate input combinations
            if all(typ == Point for typ in picked.input_types):
                # For input types that are all points
                candidates = itertools.product(all_points, repeat=len(picked.input_types))
                if picked == to_intersect and picked == construct_point_on_circle:
                    candidates = [item for item in candidates if not item[0] == construction.o]
                if picked in (construct_angle_clockwise, construct_angle_counterclockwise) and to_intersect in (construct_angle_clockwise, construct_angle_counterclockwise):
                    candidates = [item for item in candidates if not item[0] == construction.a]
                for candidate in candidates:
                    if issubclass(picked, ConstructionQ):
                        construction = picked(*candidate, diagram=diagram)
                    else:
                        construction = picked(*candidate)
                    for condition in construction.conditions():
                        if not diagram.numerical_check(condition):
                            break
                    else:
                        valid_constructions.append(construction)
            
            if not valid_constructions:
                attempt += 1
                continue

            construction = random.choice(valid_constructions)
            construction.construct(*outputs)
            constructions.append(construction)

        attempt += 1

        try:
            diagram.add_constructions(constructions, aesthetic_checking=True)
        except MaxAttemptsError:
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

    deductive_database = DeductiveDatabase(state, outer_theorems=rule_set)
    algebraic_system = AlgebraicSystem(state)
    engine = Engine(state, deductive_database, algebraic_system)
    
    try:
        with ThreadingTimeout(1200):
            engine.search(depth=10)
    except:
        return 0

    max_depth = max(state.condition2depth.values())

    if max_depth < 2:
        return 0
    
    i = 0
    conclusions = []
    conclusions += [symbol - solution for symbol, solution in state.solutions["angle_linear"].items() if len(solution.free_symbols)==0 and solution != pi/2 and solution != pi]
    conclusions += [symbol - solution for symbol, solution in state.solutions["length_ratio"].items() if len(solution.free_symbols)==0]
    conclusions += [symbol - solution for symbol, solution in state.solutions["length_linear"].items() if len(solution.free_symbols)==0]
    conclusions = [c for c in conclusions if state.condition2depth[c] >= 2 and state.condition2depth[c] <= 4 and expr_complexity(c) <= 2]
    random.shuffle(conclusions)

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
    
    for relation in conclusions:
        if isinstance(relation, Relation):
            points = relation.get_points()
        else:
            points_list = get_points_and_symbols(relation)[0]
            points = [p for points in points_list for p in points]
        
        sufficient_constructions = get_sufficient_constructions(points)
        new_state = State()
        new_state.silent = True
        symbol = list(relation.free_symbols)[0]
        goal = symbol
        answer = sympy.solve(relation, symbol)[0]
        new_state.diagram = diagram
        new_state.add_constructions(sufficient_constructions)
        variable_eqn = None
        length_related = "Length" in str(relation)
        angle_related = "Angle" in str(relation)

        if random.random() > 0.9 and (length_related or angle_related):
            rand = random.random()
            variable = random.choice(["a", "b", "c", "x", "y", "z"])
            variable = Variable(variable)
            if angle_related:
                answer = answer*180/sympy.pi
                symbol = symbol*180/sympy.pi
            
            if answer.is_integer:
                factor = random.choice([1, 2, 3, 4, 5, 6, 7])
                if random.random() > 0.5:
                    variable_eqn = variable * factor - symbol - answer%factor
                else:
                    variable_eqn = variable * factor - symbol - answer%factor + factor
                if angle_related:
                    variable_eqn *= pi
                new_state.add_equation(variable_eqn)
                answer = sympy.solve(variable_eqn.subs(symbol, answer), variable)[0]
                goal = variable
                key = goal - answer
        
        new_state.goal = goal
        new_deductive_database = DeductiveDatabase(new_state, outer_theorems=rule_set)
        new_algebraic_system = AlgebraicSystem(new_state)
        new_engine = Engine(new_state, new_deductive_database, new_algebraic_system)
        try:
            with ThreadingTimeout(1200):
                new_engine.search(depth=10)
        except:
            continue
        
        if new_state.complete() is not None:
            proof_generator = ProofGenerator(new_state, norm=0, max_equation_length_perstep=None)
            try:
                proof_generator.run()
                proof = proof_generator.get_proof()
            except:
                continue
            if len(proof) <= 4 or len(proof) >= 40:
                continue
            proof_str = proof_generator.get_proof_str(angle="degree")
            key = new_state.goal - new_state.complete()
        else:
            # requires auxiliary constructions
            continue
        
        necessary_constructions = [construction for construction in sufficient_constructions if construction in proof_generator.source_constructions[key]]
        
        # check free points
        input_points = []
        output_points = []
        for construction in necessary_constructions:
            input_points.extend(construction.inputs)
            output_points.extend(construction.outputs)
        if not all([p in output_points for p in input_points]):
            continue

        if len(necessary_constructions) <= 2:
            continue

        diagram.save()

        diagram_sample_path = os.path.join(problem_output_dir, 'diagram.png')
        diagram.save_path = diagram_sample_path

        goal_constructions = get_constructions_from_goal(relation)
        diagram.draw([], goal_constructions)
        new_state = State()
        new_state.diagram = diagram
        new_state.add_constructions(necessary_constructions)

        equations = []
        for construction in necessary_constructions:
            for conclusion in construction.conclusions():
                if isinstance(conclusion, sympy.core.expr.Expr) and len(conclusion.free_symbols)==1:
                    equations.append(conclusion)
        if variable_eqn:
            equations.append(variable_eqn)
        
        # check whether parameterized constructions are used
        conditions = []
        for step in proof:
            conditions.extend(step[0])
        if not all([eq in conditions for eq in equations]):
            continue

        diagram.draw_diagram(constructions=necessary_constructions+goal_constructions, save=True, equations=equations)
        diagram.restore()

        problem_constructions = sorted(necessary_constructions, key=lambda c: c.index)
        problem_str =  ', '.join([str(construction) for construction in problem_constructions])
        if variable_eqn:
            if 'pi' in str(variable_eqn):
                variable_eqn = variable_eqn.subs(pi, 180) / 180
            problem_str = problem_str + ', ' + str(variable_eqn)
        answer = answer.subs(pi, 180)
        
        # coordinates = []
        # for name, point in diagram.name2point.items():
        #     coordinates.append(f"{name}: ({str(point.x)}, {str(point.y)})")

        data = {
            "problem_id": problem_id,
            "seed": seed,
            "time_cost": time.time() - t0,
            "symbolic_problem": problem_str,
            "symbolic_goal": str(goal),
            "symbolic_proof": proof_str,
            "answer": str(answer),
            "diagram": diagram_sample_path,
            "depth": state.condition2depth[relation],
        }

        with open(os.path.join(problem_output_dir, "data.json"), "w") as f:
            json.dump(data, f, indent=2)
        i += 1
        break
    return i


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-problem",
        type=int,
        default=0,
        help="Maximum number of problems to generate (0 means unlimited)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="dataset/calculation",
        help="Directory to store generated problems."
    )
    args = parser.parse_args()

    max_problem = args.max_problem if args.max_problem > 0 else None
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    problem_id = 1
    while True:
        if max_problem is not None and problem_id > max_problem:
            break
        generated = generate_single_problem(problem_id=problem_id, output_dir=output_dir)
        problem_id += generated


if __name__ == '__main__':
    main()