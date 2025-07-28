import os
import sympy
import numpy as np
import json
import random
import time
import signal
import threading
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
                          timeout_handler: TimeoutHandler) -> Dict[str, Any]:
    """Generate a single problem with timeout checking at key points"""
    
    if timeout_handler.check_timeout():
        return {"samples_generated": 0, "samples_with_auxiliary": 0, "timeout": True}
    
    problem_output_dir = os.path.join(output_dir, f'rank_{rank}', f'problem_{problem_id}')
    os.makedirs(problem_output_dir, exist_ok=True)

    random.seed(42 + rank * 1000 + problem_id)
    np.random.seed(42 + rank * 1000 + problem_id)

    state = State()
    # state.silent = True
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

    # print(f"Rank {rank}: Starting problem {problem_id}")

    max_steps = random.uniform(4, 8) # 4 - 8
    max_attempt = random.uniform(50, 100)
    max_points = random.uniform(8, 12) # 8 - 12
    constructions_list = []
    index = 0

    # Construction phase with timeout checks
    while (step < max_steps and attempt < max_attempt and points < max_points 
           and not timeout_handler.check_timeout()):
        
        constructions = []
        multiconstructions = False

        if step == 0:
            candidate_set = list(construction_rule_sets["independent"])
            # candidate_set.remove(construct_free)
        else:
            rand = random.random()
            if rand < 0.3:
                candidate_set = [rule for rule in list(construction_rule_sets['deterministic']) 
                               if rule.num_inputs <= len(state.points)]
            else:
                rand = random.random()
                multiconstructions = False if rand < 0.1 else True
                candidate_set = [rule for rule in list(construction_rule_sets['nondeterministic']) 
                               if rule.num_inputs <= len(state.points)]
        
        picked = random.choice(candidate_set)
        all_points = list(state.points.copy())
        num_points = len(all_points)

        valid_constructions = []

        # Generate candidate input combinations
        if all(typ == Point for typ in picked.input_types):
            # For input types that are all points
            candidates = itertools.permutations(all_points, len(picked.input_types))
            for candidate in candidates:
                construction = picked(*candidate)
                for condition in construction.conditions():
                    if not diagram.numerical_check(condition):
                        break
                else:
                    valid_constructions.append(construction)
        else:
            # For special cases like construct_s_angle
            if picked == construct_s_angle:
                candidates = itertools.permutations(all_points, 2)
                for p1, p2 in candidates:
                    for angle in range(15, 180, 15):
                        construction = picked(p1, p2, angle)
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
        construction.construct(*outputs)
        constructions.append(construction)

        if multiconstructions:
            candidate_set = [rule for rule in list(construction_rule_sets['nondeterministic']) 
                           if rule.num_inputs <= len(state.points) and 
                           rule.num_outputs == picked.num_outputs and rule != picked]
            picked = random.choice(candidate_set)
            all_points = list(state.points.copy())
            num_points = len(all_points)

            valid_constructions = []

            # Generate candidate input combinations
            if all(typ == Point for typ in picked.input_types):
                # For input types that are all points
                candidates = itertools.product(all_points, repeat=len(picked.input_types))
                for candidate in candidates:
                    construction = picked(*candidate)
                    for condition in construction.conditions():
                        if not diagram.numerical_check(condition):
                            break
                    else:
                        valid_constructions.append(construction)
            else:
                # For special cases like construct_s_angle
                if picked == construct_s_angle:
                    candidates = itertools.product(all_points, repeat=2)
                    for p1, p2 in candidates:
                        for angle in range(15, 180, 15):
                            construction = picked(p1, p2, angle)
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
            construction.construct(*outputs)
            constructions.append(construction)

        # if attempt == 0:
        #     picked = construct_iso_triangle()
        #     picked.construct(Point('A'),Point('B'),Point('C'))
        #     constructions = [picked]
        # elif attempt == 1:
        #     picked = construct_free()
        #     picked.construct(Point('D'))
        #     constructions = [picked]
        # elif attempt == 2:
        #     picked = construct_eq_triangle(Point('A'),Point('D'))
        #     picked.construct(Point('E'))
        #     constructions = [picked]
        # elif attempt == 3:
        #     picked = construct_angle_mirror(Point('B'),Point('A'),Point('D'))
        #     picked.construct(Point('F'))
        #     picked1 = construct_on_bline(Point('D'),Point('A'))
        #     picked1.construct(Point('F'))
        #     constructions = [picked, picked1]
        # elif attempt == 4:
        #     picked = construct_trisegment(Point('A'),Point('D'))
        #     picked.construct(Point('G'), Point('H'))
        #     constructions = [picked]
        # elif attempt == 5:
        #     picked = construct_on_tline(Point('E'),Point('D'),Point('C'))
        #     picked.construct(Point('I'))
        #     constructions = [picked]
        # else:
        #     break

        attempt += 1
        try:
            diagram.add_constructions(constructions)
        except Exception as e:
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
        
        # for construction in constructions:
        #     print(construction, end=' ')
        # print()
    
    with open(os.path.join(problem_output_dir, f'constructions_list.json'), 'w') as f:
        f.write(', '.join([str(construction) for constructions in constructions_list for construction in constructions])) 

    if timeout_handler.check_timeout():
        return {"samples_generated": 0, "samples_with_auxiliary": 0, "timeout": True}

    diagram.draw_diagram(save=True)
    engine.run()

    if state.current_depth <= 2:
        return {"samples_generated": 0, "samples_with_auxiliary": 0}

    i = 0
    samples_with_auxiliary = 0
    proof_generator = ProofGenerator(state)
    # filter conclusions
    conclusions = list([relation for relation in state.relations if not trivial_condition(relation) and hasattr(relation, "source")]) + [eq for eq in state.equations 
                        if eq.sources and isinstance(eq.sources[0], InferenceRule) and not isinstance(eq.sources[0], (DiagramAngle4a, DiagramAngle4b, DiagramAngle2, FlatAngle, FlatAngle2))]
    filtered = []
    for relation in conclusions:
        if isinstance(relation, Similar3):
            points = relation.get_points()
            if Congruent3(*points) in state.relations:
                continue
        elif isinstance(relation, Parallel):
            points = relation.get_points()
            if len(set(points)) == 3:
                continue
            elif diagram.numerical_check(Collinear(*points[:3])):
                continue
        filtered.append(relation)
    
    sub_conclusions = set()
    conclusions2dir = {}

    for relation in filtered:
        if timeout_handler.check_timeout():
            break
        if isinstance(relation, Traced):
            key = relation.expr
        else:
            key = relation
        
        try:
            proof_generator.run(relation)
            proof = proof_generator.get_proof(relation)
        except Exception as e:
            continue
        
        if len(proof) <= 10 or len(proof_generator.source_constructions[key]) <= 2:
            continue

        if isinstance(relation, Relation):
            points = relation.get_points()
        else:
            points_list = get_points_and_symbols(relation)[0]
            points = [p for points in points_list for p in points]

        constructions = proof_generator.source_constructions[key]

        target_points = set(points)
        output_to_constructions = defaultdict(list)
        for c in constructions:
            for out in c.outputs:
                output_to_constructions[out].append(c)

        required = set()
        seen_points = set()

        def mark_required(point):
            if point in seen_points:
                return
            seen_points.add(point)

            for c in output_to_constructions[point]:
                if c not in required:
                    required.add(c)
                    for inp in c.inputs:
                        mark_required(inp)
        
        for point in target_points:
            mark_required(point)
        
        input_points = set()
        output_points = set()
        required_constructions = [c for c in constructions if c in required]
        for required_construction in required_constructions:
            input_points.update([p for p in required_construction.inputs if isinstance(p, Point)])
            output_points.update([p for p in required_construction.outputs])
        
        added_constructions = []
        basic_points = []
        for p in input_points:
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

        auxiliary_constructions = [c for c in constructions if c not in required]
        
        # ensure auxiliary constructions are necessary
        deleted = []
        if auxiliary_constructions:
            new_constructions = list(constructions)
            new_state = None
            for auxiliary_construction in auxiliary_constructions:
                new_constructions.remove(auxiliary_construction)
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
                    deleted.append(auxiliary_construction)
                else:
                    new_constructions.append(auxiliary_construction)
        
        if deleted:
            # change auxiliary constructions and proof_str
            auxiliary_constructions = [c for c in auxiliary_constructions if c not in deleted]
            new_proof_generator = ProofGenerator(new_state)
            new_proof_generator.run()
            proof = new_proof_generator.get_proof()
            if len(proof) <= 10 or len(new_proof_generator.source_constructions[key]) <= 2:
                continue
            proof_str = new_proof_generator.get_proof_str()
        else:
            proof_str = proof_generator.get_proof_str(relation)
        
        for (conditions, _, _) in proof:
            for cond in conditions:
                if isinstance(cond, sympy.core.expr.Expr):
                    cond = Traced(cond)
                if cond in conclusions:
                    sub_conclusions.add(cond)
            
        has_auxiliary = len(auxiliary_constructions) > 0
        if has_auxiliary:
            auxiliary_constructions = sorted(auxiliary_constructions, key=lambda c: c.index)
            aux_proof = 'Auxilirary Constructions:\n'
            for construction in auxiliary_constructions:
                aux_proof = aux_proof + str(construction) + '\n'
            proof_str = aux_proof + proof_str
            samples_with_auxiliary += 1

        diagram.save()
        if has_auxiliary:
            diagram.auxiliary_constructions.extend(auxiliary_constructions)

        sample_dir = os.path.join(problem_output_dir, f'sample_{i}')
        os.makedirs(sample_dir, exist_ok=True)

        diagram_sample_path = os.path.join(sample_dir, 'diagram.jpg')
        diagram.save_path = diagram_sample_path

        goal_constructions = get_constructions_from_goal(relation)
        diagram.draw([], goal_constructions)
        diagram.draw_diagram(constructions=required_constructions+auxiliary_constructions+goal_constructions, save=True)
        diagram.restore()

        # verify the data by construct a new diagram and generate the proof
        # new_constructions_list = []
        # for construction in sorted(added_constructions+required_constructions, key=lambda c: c.index):
        #     if not new_constructions_list:
        #         new_constructions_list.append([construction])
        #     elif all(p1 == p2 for p1, p2 in zip(new_constructions_list[-1][0].outputs,construction.outputs)):
        #         new_constructions_list[-1].append(construction)
        #     else:
        #         new_constructions_list.append([construction])
        
        # new_diagram_sample_path = os.path.join(sample_dir, 'new_diagram.jpg')
        # try:
        #     new_diagram = Diagram(constructions_list=new_constructions_list, cache_folder=None, save_path=new_diagram_sample_path)
        #     new_diagram.draw_diagram(save=True)
        # except:
        #     continue

        # new_state = State()
        # new_state.silent = True
        # new_state.goal = relation.expr if isinstance(relation, Traced) else relation
        # new_state.diagram = new_diagram
        # for new_constructions in new_constructions_list:
        #     new_state.add_constructions(new_constructions)
        # new_deductive_database = DeductiveDatabase(new_state)
        # new_algebraic_system = AlgebraicSystem(new_state)
        # new_engine = Engine(new_state, new_deductive_database, new_algebraic_system)
        # new_engine.run()

        # if not has_auxiliary and new_state.complete() is None:
        #     continue
        # if has_auxiliary and new_state.complete() is not None:
        #     continue

        # if has_auxiliary:
        #     new_auxiliary_constructions_list = []
        #     for construction in sorted(auxiliary_constructions, key=lambda c: c.index):
        #         if not new_auxiliary_constructions_list:
        #             new_auxiliary_constructions_list.append([construction])
        #         elif all(p1 == p2 for p1, p2 in zip(new_auxiliary_constructions_list[-1][0].outputs,construction.outputs)):
        #             new_auxiliary_constructions_list[-1].append(construction)
        #         else:
        #             new_auxiliary_constructions_list.append([construction])
            
        #     try:
        #         for new_auxiliary_constructions in new_auxiliary_constructions_list:
        #             new_diagram.add_constructions(new_auxiliary_constructions)
        #     except:
        #         continue

        #     new_state = State()
        #     new_state.silent = True
        #     new_state.goal = relation.expr if isinstance(relation, Traced) else relation
        #     new_state.diagram = new_diagram
        #     all_constructions_list = new_constructions_list + itgnfretkbudrthvjinghfuhulfftclilfhhdlbjblcddkgdhvikevdfhvlnkbid
        #     for new_constructions in all_constructions_list:
        #         new_state.add_constructions(new_constructions)
        #     new_deductive_database = DeductiveDatabase(new_state)
        #     new_algebraic_system = AlgebraicSystem(new_state)
        #     new_engine = Engine(new_state, new_deductive_database, new_algebraic_system)
        #     new_engine.run()
        #     if new_state.complete() is None:
        #         continue

        # new_proof_generator = ProofGenerator(new_state)
        # try:
        #     new_proof_generator.run()
        #     new_proof_str = new_proof_generator.get_proof_str()
        # except:
        #     continue

        data = {
            "problem": ', '.join([str(construction) for construction in sorted(added_constructions + required_constructions, key=lambda c: c.index)]),
            "goal": str(relation),
            "diagram": diagram_sample_path,
            "proof": proof_str,
            "rank": rank,
            "problem_id": problem_id,
            "sample_id": i,
            "has_auxiliary_constructions": has_auxiliary,
            "num_auxiliary_constructions": len(auxiliary_constructions)
        }

        with open(os.path.join(sample_dir, "data.json"), "w") as f:
            json.dump(data, f, indent=2)

        # new_data = {
        #     "problem": ', '.join([str(construction) for construction in sorted(added_constructions + required_constructions, key=lambda c: c.index)]),
        #     "goal": str(relation),
        #     "diagram": new_diagram_sample_path,
        #     "proof": new_proof_str,
        #     "rank": rank,
        #     "problem_id": problem_id,
        #     "sample_id": i,
        #     "has_auxiliary_constructions": has_auxiliary,
        #     "num_auxiliary_constructions": len(auxiliary_constructions)
        # }

        # with open(os.path.join(sample_dir, "new_data.json"), "w") as f:
        #     json.dump(new_data, f, indent=2)
        
        conclusions2dir[relation] = sample_dir
        i += 1
    
    for relation, sample_dir in conclusions2dir.items():
        if os.path.exists(os.path.join(sample_dir, "data.json")):
            with open(os.path.join(sample_dir, "data.json"), "r") as f:
                data = json.load(f)
            data["sub_conclusion"] = True if relation in sub_conclusions else False
            with open(os.path.join(sample_dir, "data.json"), "w") as f:
                json.dump(data, f, indent=2)

    print(f"Rank {rank}: Problem {problem_id} - Generated {i} samples ({samples_with_auxiliary} with auxiliary)")
    return {
        "samples_generated": i, 
        "samples_with_auxiliary": samples_with_auxiliary,
        "timeout": timeout_handler.check_timeout()
    }

def generate_until_timeout(rank: int, output_dir: str, timeout_handler: TimeoutHandler,
                          max_problem_id: Optional[int] = None) -> Dict[str, Any]:
    """Generate problems until timeout with improved progress tracking"""
    
    rank_output_dir = os.path.join(output_dir, f'rank_{rank}')
    os.makedirs(rank_output_dir, exist_ok=True)

    problem_id = 0
    total_samples = 0
    total_samples_with_auxiliary = 0
    start_time = time.time()
    problems_with_errors = 0
    problems_with_timeouts = 0

    print(f"Rank {rank}: Starting generation with timeout handler")
    if timeout_handler.timeout_seconds:
        print(f"Rank {rank}: Time limit: {timeout_handler.timeout_seconds}s")
    if max_problem_id:
        print(f"Rank {rank}: Max problems: {max_problem_id}")

    try:
        while not timeout_handler.check_timeout():
            if max_problem_id and problem_id >= max_problem_id:
                print(f"Rank {rank}: Max problem ID {max_problem_id} reached")
                break

            # try:
            result = generate_single_problem(rank, output_dir, problem_id, timeout_handler)
            
            if result.get("timeout"):
                problems_with_timeouts += 1
                print(f"Rank {rank}: Problem {problem_id} timed out")
                break
                
            if result.get("error"):
                problems_with_errors += 1
                
            total_samples += result["samples_generated"]
            total_samples_with_auxiliary += result["samples_with_auxiliary"]
            problem_id += 1
            # except KeyboardInterrupt:
            #     print(f"Rank {rank}: Keyboard interrupt received")
            #     timeout_handler.timeout_occurred = True
            #     break
            # except Exception as e:
            #     print(f"Rank {rank}: Error in problem {problem_id}: {e}")
            #     problems_with_errors += 1
            #     problem_id += 1
            #     continue
                
    except Exception as e:
        print(f"Rank {rank}: Fatal error in generation loop: {e}")
        raise

    duration = timeout_handler.get_elapsed_time()
    
    # Determine termination reason
    if timeout_handler.check_timeout():
        if problems_with_timeouts > 0:
            termination_reason = "timeout_during_problem"
        else:
            termination_reason = "timeout"
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
    
    print(f"Rank {rank}: Generation completed - {termination_reason}")
    return result

def main():
    rank = int(os.environ.get("SLURM_ARRAY_TASK_ID", "0"))
    timeout_seconds = int(os.environ.get("TIMEOUT_SECONDS", "3600"))
    max_problem_id = int(os.environ.get("MAX_PROBLEM_ID", "0"))
    base_output_dir = os.environ.get('OUTPUT_DIR', 'new_samples')
    
    os.makedirs(base_output_dir, exist_ok=True)
    
    print(f"SLURM task {rank} starting...")
    print(f"Timeout: {timeout_seconds}s, Max problems: {max_problem_id}")

    with timeout_context(timeout_seconds if timeout_seconds > 0 else None) as timeout_handler:
        result = generate_until_timeout(
            rank, base_output_dir, timeout_handler,
            max_problem_id=max_problem_id if max_problem_id > 0 else None
        )
        
        print(f"SLURM task {rank} completed: {json.dumps(result, indent=2)}")


if __name__ == '__main__':
    main()