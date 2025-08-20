import unittest
import time
import shutil

import os
from sympy import sympify

import pyeuclid.formalization.utils as utils
from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.translation import parse_texts_from_file, parse_construction_program
from pyeuclid.formalization.utils import Timeout
from pyeuclid.engine.inference_rule import inference_rule_sets
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine
import traceback
import json

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
    def test_jgex_ag_231(self):
        tot = 0
        cnt = 0
        model_path = "saves/qwen2_5-math-7b/full/sft"
        llm = LLM(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        utils.MAX_DIAGRAM_ATTEMPTS = None
        rank = int(os.environ.get("OMPI_COMM_WORLD_RANK", 0))
        world_size = int(os.environ.get("OMPI_COMM_WORLD_SIZE", 1))
        texts = parse_texts_from_file('data/IMO-AG-30.txt')
        for idx, text in enumerate(texts):
            if not idx%world_size == rank:
                continue
            state = State()
            state.silent = True
            if world_size > 1:
                state.silent = True
            try:
                constructions_list = state.load_problem_from_text(text, f'diagrams/IMO-AG-30/{idx+1}.jpg')
                os.makedirs(f'results/IMO-AG-30/{idx+1}/', exist_ok=True)
                problem_str = ', '.join([str(construction) for constructions in constructions_list for construction in constructions])
                goal_str = str(state.goal)
                data = {
                    'problem': problem_str,
                    'goal': goal_str
                }
                shutil.copy(f"diagrams/IMO-AG-30/{idx+1}.jpg", f"results/IMO-AG-30/{idx+1}/diagram.jpg")
                with open(f'results/IMO-AG-30/{idx+1}/data.json', 'w') as f:
                    json.dump(data, f, indent=4)

                if os.path.exists(f'results/IMO-AG-30/{idx+1}/new_proof.txt'):
                    continue

                if not idx in [9]: #24, 17, 25, 28, 12, 13, 5, 20, 9, 10]:
                    continue

                print(idx, text)

                # deductive_database = DeductiveDatabase(state)
                # algebraic_system = AlgebraicSystem(state)
                # proof_generator = ProofGenerator(state)
                # proof_generator.max_equation_length_perstep = None
                # engine = Engine(state, deductive_database, algebraic_system)
                # t0 = time.time()
                # t1 = None
                # with Timeout(5400):
                #     engine.search()
                #     t1 = time.time()
                #     if state.complete() is not None:
                #         print(f"{idx} solved in {t1-t0} seconds")
                #         proof_generator.run()
                #         proof_str = proof_generator.get_proof_str()
                #         print(f'{idx} proof generation runs in {time.time()-t1}')
                #         with open(f'results/IMO-AG-30/{idx+1}/proof.txt', 'w+') as f:
                #             f.write(proof_str)
                #     else:
                #         print(f"{idx} unsolved in {t1-t0} seconds")
                # if t1 is None:
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
                        print(output)
                        auxiliary_constructions = parse_construction_program(output)
                        print('passed!!!')
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

                    new_diagram = copy.deepcopy(state.diagram)
                    new_diagram.save_path = f"results/IMO-AG-30/{idx+1}/diagram.jpg"
                    try:
                        for constructions in auxiliary_constructions_list:
                            new_diagram.add_constructions(constructions)
                    except:
                        continue
                    new_diagram.draw_diagram()
                    new_state = State()
                    new_state.silent = True
                    new_state.goal = state.goal
                    new_state.diagram = new_diagram
                    for consutructions in constructions_list + auxiliary_constructions_list:
                        new_state.add_constructions(consutructions)
                    new_deductive_database = DeductiveDatabase(new_state)
                    new_algebraic_system = AlgebraicSystem(new_state)
                    new_engine = Engine(new_state, new_deductive_database, new_algebraic_system)
                    new_engine.run()
                    if new_state.complete() is not None:
                        print(idx, 'solved')
                        cnt += 1
                        # print(idx)
                        # input()
                        break
                    else:
                        print(idx, 'still not solved')
                    # print(f"{idx} unsolved in 5400 seconds")
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    exit()
                print(f"{idx} error {text}")
                print(e)
                print(traceback.format_exc())
                

if __name__ == '__main__':
    unittest.main()