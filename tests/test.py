import unittest
import time
import shutil
import copy
import os
import json
import traceback

from sympy import sympify
from collections import Counter
from stopit import ThreadingTimeout as TT

import pyeuclid.formalization.utils as utils
from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.translation import parse_texts_from_file, parse_construction_program
from pyeuclid.formalization.utils import Timeout, TimeoutException
from pyeuclid.formalization.construction_rule import *
from pyeuclid.engine.inference_rule import *
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
from pathlib import Path


system_prompt = (
    "You are an expert in plane geometry, specializing in identifying the most effective "
    "auxiliary constructions for solving geometry problems. Given a formal geometry problem, "
    "output only the essential auxiliary constructions required for the solution. "
    "Use existing points as inputs and give unique names to all newly constructed points. "
    "Each new point must be defined using no more than two auxiliary constructions."
)



class TestBenchmarks(unittest.TestCase):
    def _test_jgex_ag_231(self):
        tot = 0
        cnt = 0
        model_path = "saves/qwen2_5-math-7b/full/sft"
        llm = LLM(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        utils.MAX_DIAGRAM_ATTEMPTS = 1000
        rank = int(os.environ.get("OMPI_COMM_WORLD_RANK", 0))
        world_size = int(os.environ.get("OMPI_COMM_WORLD_SIZE", 1))
        texts = parse_texts_from_file('data/JGEX-AG-231.txt')
        for idx, text in enumerate(texts):
            if not idx%world_size == rank:
                continue
            os.makedirs(f'results/JGEX-AG-231/{idx+1}/', exist_ok=True)
            state = State()
            state.silent = True
            if world_size > 1:
                state.silent = True
            try:
                constructions_list = state.load_problem_from_text(text, f'diagrams/JGEX-AG-231/{idx+1}.jpg')
                constructions = [construction for constructions in constructions_list for construction in constructions]
                shutil.copy(f"diagrams/JGEX-AG-231/{idx+1}.jpg", f"results/JGEX-AG-231/{idx+1}/diagram.jpg")
                problem_str = ', '.join([str(construction) for construction in constructions])
                goal_str = str(state.goal)
                data = {
                    'problem': problem_str,
                    'goal': goal_str
                }
                with open(f'results/JGEX-AG-231/{idx+1}/data.json', 'w') as f:
                    json.dump(data, f, indent=4)
                
                if os.path.exists(f'results/JGEX-AG-231/{idx+1}/proof.txt'):
                    continue

                print(idx, text)

                if idx == 159:
                    continue

                tot += 1

                deductive_database = DeductiveDatabase(state)
                algebraic_system = AlgebraicSystem(state)
                proof_generator = ProofGenerator(state)
                proof_generator.max_equation_length_perstep = None
                engine = Engine(state, deductive_database, algebraic_system)
                t = time.time()
                with TT(1200):
                    engine.run()
                t = time.time() - t
                if state.complete() is not None:
                    print(f"{idx} solved in {t} seconds")
                    t0 = time.time()
                    proof = None
                    with TT(1200):
                        proof_generator.run()
                        proof = proof_generator.get_proof()
                        proof_str = proof_generator.get_proof_str()
                        max_cond_num = 0
                        acc_cond_num = 0
                        for (conditions, theorem, conclusion) in proof:
                            max_cond_num = max(max_cond_num, len(conditions))
                            acc_cond_num += len(conditions)
                    
                    if proof is not None:
                        print(f'{idx} proof generation runs in {time.time()-t0}')
                        with open(f'results/JGEX-AG-231/{idx+1}/proof.txt', 'w+') as f:
                            f.write(proof_str)
                        print(f'Proof steps: ', len(proof))
                        print(f'Max condition number: ', max_cond_num)
                        print(f'Average condition number: ', acc_cond_num / len(proof) if len(proof) > 0 else 0)
                    else:
                        print(f'{idx} proof generation fails {time.time()-t0}')
                    # if world_size == 1:
                    #     proof_generator.show_proof()
                else:
                    problem = data["problem"]
                    goal = data["goal"]

                    question = f"Problem: {problem}\nGoal: {goal}\n"

                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ]
                    prompt = tokenizer.apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                    )
                    sampling_params = llm.get_default_sampling_params()
                    sampling_params.n = 32
                    outputs = llm.generate([prompt], sampling_params)
                    sample_outputs = [o.text for o in outputs[0].outputs]
                    for output in sample_outputs:
                        try:
                            auxiliary_constructions = parse_construction_program(output)
                            auxiliary_constructions_list = []
                            for construction in auxiliary_constructions:
                                if not auxiliary_constructions_list:
                                    auxiliary_constructions_list.append([construction])
                                elif len(auxiliary_constructions_list[-1]) == len(construction.outputs) and all(o1 == o2 for o1, o2 in zip(auxiliary_constructions_list[-1][0].outputs, construction.outputs)):
                                    auxiliary_constructions_list[-1].append(construction)
                                else:
                                    auxiliary_constructions_list.append([construction])
                        except:
                            continue

                        new_state = copy.deepcopy(state)
                        new_state.diagram.save_path = f"results/JGEX-AG-231/{idx+1}/diagram.jpg"
                        try:
                            for constructions in auxiliary_constructions_list:
                                new_state.diagram.add_constructions(constructions)
                        except:
                            continue
                        new_state.diagram.draw_diagram()
                        for consutructions in constructions_list + auxiliary_constructions_list:
                            new_state.add_constructions(consutructions)
                        new_deductive_database = DeductiveDatabase(new_state)
                        new_algebraic_system = AlgebraicSystem(new_state)
                        new_engine = Engine(new_state, new_deductive_database, new_algebraic_system)
                        new_engine.run()
                        if new_state.complete() is not None:
                            print(idx, 'solved')
                            cnt += 1
                            break

            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    exit()
                print(f"{idx} error {text}")
                print(e)
                print(traceback.format_exc())
        
        print(cnt, tot, cnt/tot)
            
    def _test_jgex_without_llm(self):
        rank = int(os.environ.get("OMPI_COMM_WORLD_RANK", 0))
        world_size = int(os.environ.get("OMPI_COMM_WORLD_SIZE", 1))
        texts = parse_texts_from_file('data/JGEX-AG-231.txt')
        for idx, text in enumerate(texts):
            if not idx%world_size == rank:
                continue
            os.makedirs(f'results/JGEX-AG-231/{idx+1}/', exist_ok=True)
            state = State()
            state.silent = True
            if world_size > 1:
                state.silent = True
            try:
                state.load_problem_from_text(text, f'diagrams/JGEX-AG-231/{idx+1}.jpg')
                shutil.copy(f"diagrams/JGEX-AG-231/{idx+1}.jpg", f"results/JGEX-AG-231/{idx+1}/diagram.jpg")
                deductive_database = DeductiveDatabase(state)
                algebraic_system = AlgebraicSystem(state)
                proof_generator = ProofGenerator(state)
                engine = Engine(state, deductive_database, algebraic_system)
                t = time.time()
                with TT(1200):
                    engine.run()
                t = time.time() - t
                if state.complete() is not None:
                    print(f"{idx} solved in {t} seconds")
                    t0 = time.time()
                    proof = None
                    with TT(1200):
                        proof_generator.run()
                        proof = proof_generator.get_proof()
                        proof_str = proof_generator.get_proof_str()
                        max_cond_num = 0
                        acc_cond_num = 0
                        for (conditions, theorem, conclusion) in proof:
                            max_cond_num = max(max_cond_num, len(conditions))
                            acc_cond_num += len(conditions)
                    
                    if proof is not None:
                        print(f'{idx} proof generation runs in {time.time()-t0}')
                        with open(f'results/JGEX-AG-231/{idx+1}/proof.txt', 'w+') as f:
                            f.write(proof_str)
                        print(f'Proof steps: ', len(proof))
                        print(f'Max condition number: ', max_cond_num)
                        print(f'Average condition number: ', acc_cond_num / len(proof) if len(proof) > 0 else 0)
                    else:
                        print(f'{idx} proof generation fails {time.time()-t0}')
                    # if world_size == 1:
                    #     proof_generator.show_proof()
                else:
                    print(f"{idx} unsolved in {t} seconds")
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    exit()
                print(f"{idx} error {text}")
                print(e)
                print(traceback.format_exc())
            
    def test_geometry3k(self):
        rank = int(os.environ.get("OMPI_COMM_WORLD_RANK", 0))
        world_size = int(os.environ.get("OMPI_COMM_WORLD_SIZE", 1))
        for idx in range(2401, 3002):
            if not idx%world_size == rank:
                continue
            if not os.path.isfile(f"data/Geometry3K/{idx}/problem.py"):
                continue
            namespace = {}
            try:
                with open(f'data/Geometry3K/{idx}/problem.py', "r") as file:
                    exec(file.read(), namespace)
                conditions = namespace.get("conditions")
                goal = namespace.get("goal")
                solution = namespace.get("solution")
                diagrammatic_relations = namespace.get("new_diagrammatic_relations")
                for i in conditions:
                    if isinstance(i, Between):
                        diagrammatic_relations.discard(NotCollinear(i.p1,i.p2,i.p3))
                state = State()
                state.silent = True
                state.load_problem(conditions=conditions, goal=goal)
                state.add_conditions(list(diagrammatic_relations))
                
                deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['complex']+inference_rule_sets["basic"])
                algebraic_system = AlgebraicSystem(state)
                proof_generator = ProofGenerator(state)
                engine = Engine(state, deductive_database, algebraic_system)
                try:
                    t = time.time()
                    with Timeout(600) as tt:
                        engine.run()
                    result = state.complete()
                    t = time.time() - t
                except Exception as e:
                    raise e
                result = state.complete()
                
                if result is not None:
                    if (result is True or abs((sympify(result).evalf() - sympify(solution).evalf()) / (sympify(solution).evalf() + 1e-4)) < 2e-2):
                        print(f"{idx} solved in {t} seconds")
                    else:
                        print(f"{idx} wrong solution in {t} seconds")
                    proof = proof_generator.get_proof_str()
                    if world_size == 1:
                        print(proof)
                else:
                    print(f"{idx} unsolved in {t} seconds")
                break
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    exit()
                print(f"{idx} error {e}")
                print(traceback.format_exc())
    
if __name__ == '__main__':
    unittest.main()