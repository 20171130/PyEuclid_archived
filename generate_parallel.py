import os
import sympy
import numpy as np
import json
import random
import time
import signal

from pyeuclid.formalization.diagram import Diagram
from pyeuclid.formalization.state import State
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.translation import get_constructions_from_goal
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

class TimeoutHandler:
    def __init__(self):
        self.timeout_occurred = False

    def timeout_handler(self, signum, frame):
        self.timeout_occurred = True
        print("Timeout signal received")

def generate_single_problem(rank, output_dir, problem_id):
    problem_output_dir = os.path.join(output_dir, f'rank_{rank}', f'problem_{problem_id}')
    os.makedirs(problem_output_dir, exist_ok=True)

    random.seed(42 + rank * 1000 + problem_id)
    np.random.seed(42 + rank * 1000 + problem_id)

    state = State()
    state.silent = True
    deductive_database = DeductiveDatabase(state)
    algebraic_system = AlgebraicSystem(state)
    engine = Engine(state, deductive_database, algebraic_system)

    diagram_path = os.path.join(problem_output_dir, f'diagram_rank_{rank}_problem_{problem_id}.jpg')
    diagram = Diagram(cache_folder=None, save_path=diagram_path)
    state.diagram = diagram

    depth = 0
    attempt = 0
    points = 0

    print(f"Rank {rank}: Starting problem {problem_id}")

    max_depth = random.uniform(6, 10)
    max_attempt = random.uniform(50, 100)
    max_points = random.uniform(8, 12)

    while depth < max_depth and attempt < max_attempt and points < max_points:
        constructions = []
        multiconstructions = False

        if depth == 0:
            candidate_set = construction_rule_sets["independent"]
            candidate_set.remove(construct_free)
            candidate_set = [construct_r_triangle]
        else:
            rand = random.random()
            if rand < 0.02:
                candidate_set = [construct_free]
            elif rand < 0.31:
                candidate_set = [rule for rule in construction_rule_sets['deterministic'] if rule.num_inputs <= len(state.points)]
            else:
                multiconstructions = True
                candidate_set = [rule for rule in construction_rule_sets['nondeterministic'] if rule.num_inputs <= len(state.points)]

        picked = random.choice(candidate_set)
        all_points = list(state.points.copy())
        num_points = len(all_points)
        random.shuffle(all_points)
        inputs = []
        for type in picked.input_types:
            if type == Point:
                inputs.append(all_points.pop())
            else:
                if picked == construct_s_angle:
                    inputs.append(random.choice(range(15, 180, 15)))
        outputs = [Point(chr(ord('A') + num_points + i)) for i in range(picked.num_outputs)]
        construction = picked(*inputs)
        construction.construct(*outputs)
        constructions.append(construction)

        if multiconstructions:
            candidate_set = [rule for rule in construction_rule_sets['nondeterministic'] if rule.num_inputs <= len(state.points) and rule.num_outputs == picked.num_outputs and rule != picked]
            picked = random.choice(candidate_set)
            all_points = list(state.points.copy())
            num_points = len(all_points)
            random.shuffle(all_points)
            inputs = []
            for type in picked.input_types:
                if type == Point:
                    inputs.append(all_points.pop())
                else:
                    if picked == construct_s_angle:
                        inputs.append(random.choice(range(15, 180, 15)))
            outputs = [Point(chr(ord('a') + num_points + i)) for i in range(picked.num_outputs)]
            construction = picked(*inputs)
            construction.construct(*outputs)
            constructions.append(construction)

        attempt += 1
        try:
            diagram.add_constructions(constructions)
        except:
            continue

        state.add_constructions(constructions)
        depth += 1
        points += len(outputs)

        for construction in constructions:
            print(f"Rank {rank}: Problem {problem_id} - {construction.index} {construction}")

    diagram.draw_diagram(save=True)
    engine.run()

    if state.current_depth <= 3:
        print(f"Rank {rank}: Problem {problem_id} - Early termination - depth too low")
        return {"samples_generated": 0, "samples_with_auxiliary": 0}

    i = 0
    samples_with_auxiliary = 0
    proof_generator = ProofGenerator(state)
    dd_derived = list(state.dd_conclusions) + list(state.relations)

    print(f"Rank {rank}: Problem {problem_id} - Processing {len(dd_derived)} relations")

    for relation in dd_derived:
        proof_generator.run(relation)

        if isinstance(relation, Traced):
            key = relation.str_rep
        else:
            key = relation

        if state.condition2depth[key] <= 3 or len(proof_generator.source_constructions[key]) <= 2:
            continue

        if isinstance(relation, Relation):
            points = relation.get_points()
        else:
            points_list = get_points_and_symbols(relation)[0]
            points = [p for points in points_list for p in points]

        constructions = proof_generator.source_constructions[key]
        auxilirary_constructions = []
        required_points = set(points)

        for construction in constructions:
            if any(p in construction.outputs for p in points):
                required_points.update(construction.inputs)

        for construction in constructions:
            if all(p not in required_points for p in construction.outputs):
                auxilirary_constructions.append(construction)

        proof_str = proof_generator.get_proof_str(relation)
        has_auxiliary = len(auxilirary_constructions) > 0

        if has_auxiliary:
            auxilirary_constructions = sorted(auxilirary_constructions, key=lambda c: c.index)
            aux_proof = 'Auxilirary Constructions:\n'
            for construction in auxilirary_constructions:
                aux_proof = aux_proof + str(construction) + '\n'
            proof_str = aux_proof + proof_str
            samples_with_auxiliary += 1

        diagram.save()
        if has_auxiliary:
            diagram.auxiliary_constructions.extend(auxilirary_constructions)

        sample_dir = os.path.join(problem_output_dir, f'sample_{i}')
        os.makedirs(sample_dir, exist_ok=True)

        diagram_sample_path = os.path.join(sample_dir, 'diagram.jpg')
        diagram.save_path = diagram_sample_path

        goal_constructions = get_constructions_from_goal(relation)
        diagram.draw([], goal_constructions)
        diagram.draw_diagram(constructions=constructions+goal_constructions, save=True)
        diagram.restore()

        data = {
            "problem": ', '.join([str(construction) for construction in constructions]),
            "goal": str(relation),
            "diagram": diagram_sample_path,
            "proof": proof_str,
            "rank": rank,
            "problem_id": problem_id,
            "sample_id": i,
            "has_auxiliary_constructions": has_auxiliary,
            "num_auxiliary_constructions": len(auxilirary_constructions)
        }

        with open(os.path.join(sample_dir, "data.json"), "w") as f:
            json.dump(data, f, indent=2)
        i += 1

    print(f"Rank {rank}: Problem {problem_id} - Generated {i} samples ({samples_with_auxiliary} with auxiliary)")
    return {"samples_generated": i, "samples_with_auxiliary": samples_with_auxiliary}

def generate_until_timeout(rank, output_dir, timeout_handler, max_timeout_seconds=None, max_problem_id=None):
    rank_output_dir = os.path.join(output_dir, f'rank_{rank}')
    os.makedirs(rank_output_dir, exist_ok=True)

    problem_id = 0
    total_samples = 0
    total_samples_with_auxiliary = 0
    start_time = time.time()

    if max_timeout_seconds:
        local_timeout = start_time + max_timeout_seconds
    else:
        local_timeout = None

    try:
        while not timeout_handler.timeout_occurred:
            if local_timeout and time.time() > local_timeout:
                print(f"Rank {rank}: Local timeout reached")
                break

            if max_problem_id and problem_id >= max_problem_id:
                print(f"Rank {rank}: Max problem ID {max_problem_id} reached")
                break

            try:
                result = generate_single_problem(rank, output_dir, problem_id)
                total_samples += result["samples_generated"]
                total_samples_with_auxiliary += result["samples_with_auxiliary"]
                problem_id += 1
            except Exception as e:
                print(f"Rank {rank}: Error in problem {problem_id}: {e}")
                problem_id += 1
                continue
    except Exception as e:
        print(f"Rank {rank}: Fatal error in generation loop: {e}")
        raise

    duration = time.time() - start_time
    return {
        "total_samples": total_samples,
        "total_problems": problem_id,
        "samples_with_auxiliary": total_samples_with_auxiliary,
        "termination_reason": "completed",
        "duration": duration
    }

def main():
    rank = int(os.environ.get("SLURM_ARRAY_TASK_ID", "0"))

    timeout_seconds = int(os.environ.get("TIMEOUT_SECONDS", "3600"))
    max_problem_id = int(os.environ.get("MAX_PROBLEM_ID", "0"))

    timeout_handler = TimeoutHandler()
    signal.signal(signal.SIGTERM, timeout_handler.timeout_handler)
    signal.signal(signal.SIGINT, timeout_handler.timeout_handler)

    base_output_dir = os.environ.get('OUTPUT_DIR', 'samples')
    os.makedirs(base_output_dir, exist_ok=True)

    print(f"SLURM task {rank} starting...")

    result = generate_until_timeout(
        rank, base_output_dir, timeout_handler,
        max_timeout_seconds=timeout_seconds if timeout_seconds > 0 else None,
        max_problem_id=max_problem_id if max_problem_id > 0 else None
    )

    print(f"SLURM task {rank} completed: {json.dumps(result, indent=2)}")

if __name__ == '__main__':
    main()
