import os
import sympy
import numpy as np
import json
import random
from typing import Optional, Dict, Any
import time
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.diagram import Diagram, MaxAttemptsError
from pyeuclid.formalization.state import State
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.translation import get_constructions_from_goal
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.inference_rule import *
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

from pyeuclid.formalization.construction_q import ConstructionQ, construct_segment_q, construct_square_q, construct_rectangle_q, construct_angle_counterclockwise, construct_angle_clockwise, construct_point_on_circle, construct_point_on_line, construct_parallelogram_q, construct_eq_trapezoid_q, construct_r_triangle_q, construct_eq_triangle_q, construct_ieq_triangle_q, construct_r_trapezoid_q


# import logging
# Configure basic logging to console
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# # Get a logger
# logger = logging.getLogger(__name__)

from datetime import datetime
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
    
def printt(s):
    # Get the current date and time
    now = datetime.now()
    # Format the time as a string (e.g., HH:MM:SS)
    current_time_str = now.strftime("%H:%M:%S")
    # Print the formatted time
    s = f"Rank {rank} {current_time_str} {s}"
    print(s)


debug = True
problem_type = "calculation"

def generate_single_problem(rank: int, output_dir: str, problem_id: int) -> Dict[str, Any]:
    """Generate a single problem with timeout checking at key points"""
    
    problem_output_dir = os.path.join(output_dir, f'rank_{rank}', f'problem_{problem_id}')
    os.makedirs(problem_output_dir, exist_ok=True)

    seed = random.randint(0, int(1e9))
    hash_seed = os.environ.get("PYTHONHASHSEED", None)
    assert hash_seed is not None
    random.seed(seed)
    np.random.seed(seed)
    sympy.core.random.seed(seed)
    printt(f"Seed: {seed} Hash Seed: {hash_seed}")

    state = State()
    state.silent = True
    point2constructions = {}

    diagram_path = os.path.join(problem_output_dir, f'diagram_rank_{rank}_problem_{problem_id}.pdf')
    
    diagram = Diagram(cache_folder=None, save_path=diagram_path)
    state.diagram = diagram

    step = 0
    attempt = 0
    points = 0
    t0 = time.time()
    
    # printt(f"Rank {rank}: Starting problem {problem_id}")
    if problem_type == "proving":
        max_steps = random.uniform(4, 10) # 4 - 10
        max_points = random.uniform(8, 15) # 8 - 15
        rule_set = inference_rule_sets["basic"]
    else:
        max_steps = random.uniform(3, 6) # 4 - 10
        max_points = 8
        rule_set = inference_rule_sets["basic"]+inference_rule_sets['complex']
        rule_set = [item for item in rule_set if not item in (LawOfSines, LawOfCosines)]
    
    max_attempts = 100
    constructions_list = []
    length_values, angle_values = set(), set()
    index = 0
        
    construction_rule_set = [construct_segment_q, construct_r_triangle_q, construct_eq_triangle_q, construct_ieq_triangle_q, construct_r_trapezoid_q, construct_eq_trapezoid_q, construct_square_q, construct_rectangle_q, construct_parallelogram_q]
    construction_rule_set += [construct_angle_counterclockwise, construct_angle_clockwise, construct_point_on_circle, construct_point_on_line, construct_on_dia, construct_angle_bisector, construct_circumcenter, construct_eqdistance, construct_incenter, construct_intersection_cc, construct_intersection_lc, construct_intersection_ll, construct_intersection_lp, construct_intersection_lt, construct_intersection_pp, construct_intersection_tt, construct_lc_tangent, construct_midpoint, construct_mirror, construct_on_aline, construct_on_bline, construct_on_circle, construct_on_line, construct_on_pline, construct_on_tline, construct_orthocenter, construct_reflect]
    construction_rule_set += [construct_foot] * 10
    # the diagram is fully determined
    if debug:
        state.silent = False
    # Construction phase with timeout checks
    while (step < max_steps and attempt < max_attempts and len(state.points)<max_points):
        
        constructions = []
        multiconstructions = False

        if step == 0:
            candidate_set = [rule for rule in construction_rule_set if rule in construction_rule_sets["independent"]]
        else:
            rand = random.random()
            if rand < 0.3:
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
        outputs = [Point(chr(ord('A') + num_points + i)) for i in range(picked.num_outputs)]
        results = construction.construct(*outputs)
        if not results is None:
            a, b = results
            length_values = length_values.union(a)
            angle_values = angle_values.union(b)
        constructions.append(construction)

        if multiconstructions:
            to_intersect = picked
            candidate_set = [rule for rule in  construction_rule_set if rule.num_inputs <= len(state.points) and rule.num_outputs == picked.num_outputs and rule in construction_rule_sets['nondeterministic']]
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
            diagram.add_constructions(constructions)
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
        
        equations = [item.expr for item in state.equations if len(item.free_symbols)==1]
        annotated_equations = diagram.draw_diagram(save=True, equations=equations)

    with open(os.path.join(problem_output_dir, f'constructions_list.json'), 'w') as f:
        s = ', '.join([str(construction) for constructions in constructions_list for construction in constructions])
        f.write(s)
    printt(s)
    deductive_database = DeductiveDatabase(state, outer_theorems=rule_set)
    algebraic_system = AlgebraicSystem(state)
    engine = Engine(state, deductive_database, algebraic_system)
    proof_generator = ProofGenerator(state)
    engine.run()

    i = 0
    samples_with_auxiliary = 0
    sub_conclusions = set()
    conclusions2dir = {}
    conclusions = []
    if problem_type == "proving":
        conclusions = list([relation for relation in state.relations if not trivial_condition(relation) and hasattr(relation, "source")]) 
        conclusions += [eq for eq in state.equations if eq.sources and isinstance(eq.sources[0], InferenceRule) and not isinstance(eq.sources[0], (DiagramAngle4a, DiagramAngle4b, DiagramAngle2, FlatAngle, FlatAngle2))]
    else:
        conclusions = [item.expr for item in state.equations if len(item.expr.free_symbols)==1]
    printt("Determining if auxiliary constructions are needed")
    sample_dir = os.path.join(problem_output_dir, f'sample_{i}')
    os.makedirs(sample_dir, exist_ok=True)
    conclusions.sort(key=lambda x: -state.condition2depth[x])
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
        new_state = State()
        new_state.silent = True
        new_state.goal = relation.expr if isinstance(relation, Traced) else relation
        new_state.diagram = diagram
        new_state.add_constructions(sufficient_constructions)
        new_deductive_database = DeductiveDatabase(new_state, outer_theorems=rule_set)
        new_algebraic_system = AlgebraicSystem(new_state)
        new_engine = Engine(new_state, new_deductive_database, new_algebraic_system)
        new_engine.run()
        
        if new_state.complete() is not None:
            auxiliary_constructions = []
            new_proof_generator = ProofGenerator(new_state)
            new_proof_generator.run()
            new_proof = new_proof_generator.get_proof()
            new_proof_str = new_proof_generator.get_proof_str()
        else:
            # requires auxiliary constructions
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
            printt("Pruning auxiliary constructions")
            for auxiliary_construction in sufficient_auxiliary_constructions[::-1]:
                new_auxiliary_constructions = auxiliary_constructions.copy()
                new_auxiliary_constructions.remove(auxiliary_construction)
                new_constructions = sufficient_constructions + new_auxiliary_constructions
                new_state = State()
                new_state.silent = True
                new_state.goal = relation.expr if isinstance(relation, Traced) else relation
                new_state.diagram = diagram
                new_state.add_constructions(new_constructions)
                new_deductive_database = DeductiveDatabase(new_state, outer_theorems=rule_set)
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
            new_deductive_database = DeductiveDatabase(new_state, outer_theorems=rule_set)
            new_algebraic_system = AlgebraicSystem(new_state)
            new_engine = Engine(new_state, new_deductive_database, new_algebraic_system)
            new_engine.run()
            assert new_state.complete() is not None
            new_proof_generator = ProofGenerator(new_state)
            new_proof_generator.run()
            new_proof = new_proof_generator.get_proof()
            new_proof_str = new_proof_generator.get_proof_str()
            break
        
        necessary_constructions = [construction for construction in sufficient_constructions if construction in new_proof_generator.source_constructions[key]]
        
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
            aux_proof = 'Auxilirary Constructions:\n'
            for construction in auxiliary_constructions:
                aux_proof = aux_proof + str(construction) + '\n'
            new_proof_str = aux_proof + new_proof_str
            samples_with_auxiliary += 1

        diagram.save()
        if has_auxiliary:
            diagram.auxiliary_constructions.extend(auxiliary_constructions)

        sample_dir = os.path.join(problem_output_dir, f'sample_{i}')
        os.makedirs(sample_dir, exist_ok=True)

        diagram_sample_path = os.path.join(sample_dir, 'diagram.pdf')
        diagram.save_path = diagram_sample_path

        goal_constructions = get_constructions_from_goal(relation)
        diagram.draw([], goal_constructions)
        new_state = State()
        new_state.diagram = diagram
        new_state.add_constructions(necessary_constructions+auxiliary_constructions)
        goal = str(relation)
        equations = [item.expr for item in new_state.equations if len(item.free_symbols)==1]
        if "Length" in str(relation) or "Angle" in str(relation):
            rand = random.random()
            symbol = list(relation.free_symbols)[0]
            value = sympy.solve(relation, symbol)[0]
            variable = random.choice(["a", "b", "c", "x", "y", "z"])
            variable = Variable(variable)
            if "Angle" in str(relation):
                value = value/sympy.pi*180
                symbol = symbol *180/sympy.pi
            factor = random.choice([1, 2, 3, 4, 5, 6, 7])
            if random.random() > 0.5:
                equation = variable * factor - symbol - value%factor
            else:
                equation = variable * factor - symbol - value%factor + factor
            equations.append(equation)
            goal = str(equation.subs(symbol, value)/factor)
        annotated_equations = diagram.draw_diagram(constructions=necessary_constructions+auxiliary_constructions+goal_constructions, save=True, equations=equations)
        diagram.restore()

        problem_constructions = sorted(necessary_constructions+added_constructions, key=lambda c: c.index)

        data = {
            "problem": ', '.join([str(construction) for construction in problem_constructions]),
            "necessary_constructions": ', '.join([str(construction) for construction in necessary_constructions]),
            "unused_constructions": ', '.join([str(construction) for construction in sufficient_constructions if construction not in necessary_constructions]),
            "auxiliary_constructions": ', '.join([str(construction) for construction in auxiliary_constructions]),
            "goal": goal,
            "depth": state.condition2depth[relation],
            "diagram": diagram_sample_path,
            "proof": new_proof_str,
            "rank": rank,
            "time_cost": time.time() - t0,
            "problem_id": problem_id,
            "sample_id": i,
            "seed": seed,
            "hash_seed": hash_seed,
            "annotated_equations": [str(item) for item in annotated_equations],
            "has_auxiliary_constructions": has_auxiliary,
            "num_auxiliary_constructions": len(auxiliary_constructions)
        }

        with open(os.path.join(sample_dir, "data.json"), "w") as f:
            json.dump(data, f, indent=2)
        
        conclusions2dir[relation] = sample_dir
        i += 1
        break
    
    for relation, sample_dir in conclusions2dir.items():
        if os.path.exists(os.path.join(sample_dir, "data.json")):
            with open(os.path.join(sample_dir, "data.json"), "r") as f:
                data = json.load(f)
            data["sub_conclusion"] = True if relation in sub_conclusions else False
            with open(os.path.join(sample_dir, "data.json"), "w") as f:
                json.dump(data, f, indent=2)
                
    printt(f"Rank {rank}: Problem {problem_id} - Generated {i} samples ({samples_with_auxiliary} with auxiliary)")

def main():
    max_problem_id = int(os.environ.get("MAX_PROBLEM_ID", "100"))
    base_output_dir = os.environ.get('OUTPUT_DIR', 'new_samples')

    os.makedirs(base_output_dir, exist_ok=True)
    for problem_id in range(max_problem_id):
        generate_single_problem(rank=rank, problem_id=problem_id, output_dir=base_output_dir)


if __name__ == '__main__':
    main()