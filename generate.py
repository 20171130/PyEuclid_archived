import os
import json
import random

from pyeuclid.formalization.diagram import Diagram
from pyeuclid.formalization.state import State
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.translation import get_constructions_from_goal
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine
import tqdm


def generate():
    # array_task_id = int(os.environ["SLURM_ARRAY_TASK_ID"])
    # os.makedirs(f'samples/{array_task_id}/')

    state = State()
    # state.silent = True
    deductive_database = DeductiveDatabase(state)
    algebraic_system = AlgebraicSystem(state)
    engine = Engine(state, deductive_database, algebraic_system)
    diagram = Diagram(cache_folder=None, save_path=os.path.join(ROOT_DIR, 'samples/test.jpg'))
    state.diagram = diagram
    
    depth = 0
    attempt = 0
    points = 0
    
    
    while depth < 5 and attempt < 20 and points < 10:
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
            elif rand < 0.51:
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
        outputs = [Point(chr(ord('a') + num_points + i)) for i in range(picked.num_outputs)]
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
            print(construction.index, construction)
    
    diagram.draw_diagram(save=True)
    engine.run()

    i = 0
    def generate_data(goal):
        nonlocal i
        if isinstance(goal, Relation):  
            points = goal.get_points()
        else:
            points_list = get_points_and_symbols(goal)[0]
            print('points_list', points_list)
            points = [p for points in points_list for p in points]
            print('points', points)

        
        constructions = proof_generator.source_constructions[goal]
        auxilirary_constructions = []
        required_points = set(points)

        for construction in constructions:
            if any(p in construction.outputs for p in points):
                required_points.update(construction.inputs)
        
        for construction in constructions:
            if all(p not in required_points for p in construction.outputs):
                auxilirary_constructions.append(construction)

        proof_str = proof_generator.get_proof_str(goal)
        if auxilirary_constructions:
            auxilirary_constructions = sorted(auxilirary_constructions, key=lambda c: c.index)
            aux_proof = 'Auxilirary Constructions:\n'
            for construction in auxilirary_constructions:
                aux_proof = aux_proof + str(construction) + '\n'
            proof_str = aux_proof + proof_str

        diagram.save()
        proof = proof_generator.get_proof(goal)        
        diagram.auxiliary_constructions.extend(auxilirary_constructions)
        diagram_path = os.path.join(ROOT_DIR, f'samples/{i}/diagram.jpg')
        diagram.save_path = diagram_path
        goal_constructions = get_constructions_from_goal(goal)
        diagram.draw([], goal_constructions)
        diagram.draw_diagram(constructions=constructions+goal_constructions, save=True)
        diagram.restore()
        
        data_path = os.path.join(ROOT_DIR, f'samples/{i}/')
        data = {
            "problem": ', '.join([str(construction) for construction in constructions]),
            "goal": str(goal),
            "diagram": diagram_path,
            "proof": proof_str,
        }

        with open(f"{data_path}/data.json", "w") as f:
            json.dump(data, f, indent=2)
        i += 1
    
    proof_generator = ProofGenerator(state)

    for depth in tqdm.tqdm(range(state.current_depth, 0, -1)): # no need to trace depth 0
        for cond in tqdm.tqdm(state.depth2conditions[depth]):
            proof_generator.run(cond)
            proof_generator.track_constructions(cond)
    
    end_relations = proof_generator.find_end_nodes()
    print('end_relations', end_relations)
    input()

    for relation in end_relations:
        proof_generator.track_constructions(relation)
        if state.condition2depth[relation] <= 2 and len(proof_generator.source_constructions[relation]) <= 2:
            continue
        print(relation)
        print(state.condition2depth[relation])
        input()
        generate_data(relation)

        
if __name__ == '__main__':
    generate()