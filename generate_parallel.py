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

from pyeuclid.formalization.diagram import Diagram
from pyeuclid.formalization.state import State
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.translation import get_constructions_from_goal
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.inference_rule import InferenceRule
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
    deductive_database = DeductiveDatabase(state)
    algebraic_system = AlgebraicSystem(state)
    engine = Engine(state, deductive_database, algebraic_system)

    diagram_path = os.path.join(problem_output_dir, f'diagram_rank_{rank}_problem_{problem_id}.jpg')
    diagram = Diagram(cache_folder=None, save_path=diagram_path)
    print(diagram_path)
    state.diagram = diagram

    step = 0
    attempt = 0
    points = 0

    print(f"Rank {rank}: Starting problem {problem_id}")

    max_steps = random.uniform(4, 8)
    max_attempt = random.uniform(50, 100)
    max_points = random.uniform(8, 12)

    # Construction phase with timeout checks
    while (step < max_steps and attempt < max_attempt and points < max_points 
           and not timeout_handler.check_timeout()):
        
        constructions = []
        multiconstructions = False

        if step == 0:
            candidate_set = list(construction_rule_sets["independent"])
            candidate_set.remove(construct_free)
        else:
            rand = random.random()
            if rand < 0.02:
                candidate_set = [construct_free]
            elif rand < 0.31:
                candidate_set = [rule for rule in list(construction_rule_sets['deterministic']) 
                               if rule.num_inputs <= len(state.points)]
            else:
                multiconstructions = True
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

        attempt += 1
        try:
            
            diagram.add_constructions(constructions)
        except Exception as e:
            # print(f"Rank {rank}: Problem {problem_id} - Construction failed: {e}")
            continue

        state.add_constructions(constructions)
        step += 1
        points += len(outputs)

        for construction in constructions:
            print(construction, end=' ')
        print()

    # Early timeout check
    if timeout_handler.check_timeout():
        return {"samples_generated": 0, "samples_with_auxiliary": 0, "timeout": True}

    try:
        diagram.draw_diagram(save=True)
        engine.run()
    except Exception as e:
        # print(f"Rank {rank}: Problem {problem_id} - Engine run failed: {e}")
        return {"samples_generated": 0, "samples_with_auxiliary": 0, "error": str(e)}

    if state.current_depth <= 3:
        # print(f"Rank {rank}: Problem {problem_id} - Early termination - depth too low")
        return {"samples_generated": 0, "samples_with_auxiliary": 0}

    i = 0
    samples_with_auxiliary = 0
    proof_generator = ProofGenerator(state)
    conclusions = list([relation for relation in state.relations if hasattr(relation, "source")]) + [eq for eq in state.equations 
                                         if eq.sources and isinstance(eq.sources[0], InferenceRule)]

    # print(f"Rank {rank}: Problem {problem_id} - Processing {len(conclusions)} relations")

    # Process relations with timeout checks
    for relation in conclusions:
        if timeout_handler.check_timeout():
            print(f"Rank {rank}: Problem {problem_id} - Timeout during relation processing")
            break
            
        try:
            proof_generator.run(relation)
        except Exception as e:
            print(f"Rank {rank}: Problem {problem_id} - Proof generation failed: {e}")
            continue

        if isinstance(relation, Traced):
            key = relation.expr
        else:
            key = relation

        print(relation)
        input()

        if state.condition2depth[key] <= 2 or len(proof_generator.source_constructions[key]) <= 2:
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

        try:
            proof_str = proof_generator.get_proof_str(relation)
        except Exception as e:
            print(f"Rank {rank}: Problem {problem_id} - Proof string generation failed: {e}")
            continue
            
        has_auxiliary = len(auxilirary_constructions) > 0

        if has_auxiliary:
            auxilirary_constructions = sorted(auxilirary_constructions, key=lambda c: c.index)
            aux_proof = 'Auxilirary Constructions:\n'
            for construction in auxilirary_constructions:
                aux_proof = aux_proof + str(construction) + '\n'
            proof_str = aux_proof + proof_str
            samples_with_auxiliary += 1

        try:
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
            
        except Exception as e:
            print(f"Rank {rank}: Problem {problem_id} - Sample {i} generation failed: {e}")
            continue

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

            # Progress reporting
            if problem_id > 0 and problem_id % 10 == 0:
                elapsed = timeout_handler.get_elapsed_time()
                remaining = timeout_handler.get_remaining_time()
                rate = problem_id / elapsed if elapsed > 0 else 0
                print(f"Rank {rank}: Progress - {problem_id} problems, {total_samples} samples, "
                      f"{rate:.2f} problems/s, elapsed: {elapsed:.1f}s"
                      + (f", remaining: {remaining:.1f}s" if remaining else ""))

            try:
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
                
            except KeyboardInterrupt:
                print(f"Rank {rank}: Keyboard interrupt received")
                timeout_handler.timeout_occurred = True
                break
            except Exception as e:
                print(f"Rank {rank}: Error in problem {problem_id}: {e}")
                problems_with_errors += 1
                problem_id += 1
                continue
                
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
    base_output_dir = os.environ.get('OUTPUT_DIR', 'samples')
    
    os.makedirs(base_output_dir, exist_ok=True)
    
    print(f"SLURM task {rank} starting...")
    print(f"Timeout: {timeout_seconds}s, Max problems: {max_problem_id}")

    try:
        with timeout_context(timeout_seconds if timeout_seconds > 0 else None) as timeout_handler:
            result = generate_until_timeout(
                rank, base_output_dir, timeout_handler,
                max_problem_id=max_problem_id if max_problem_id > 0 else None
            )
            
            print(f"SLURM task {rank} completed: {json.dumps(result, indent=2)}")
            
    except KeyboardInterrupt:
        print(f"SLURM task {rank} interrupted by user")
    except Exception as e:
        print(f"SLURM task {rank} failed with error: {e}")
        raise

if __name__ == '__main__':
    main()