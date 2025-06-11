import os
import random

from pyeuclid.formalization.diagram import Diagram
from pyeuclid.formalization.state import State
from pyeuclid.formalization.construction_rule import *
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine


def generate():
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
    
    
    while depth < 3 and attempt < 20 and points < 8:
        constructions = []
        multiconstructions = False
        
        if depth == 0:
            candidate_set = construction_rule_sets["independent"]
        else:
            rand = random.random()
            if rand < 0.02:
                candidate_set = construction_rule_sets["independent"]
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
            print(construction)
    
    diagram.draw_diagram(save=True)
    engine.search()

    def trace_constructions_list(points):
        constructions_list = []
        visited = set()
        queue = points.copy()

        while queue:
            p = queue.pop()
            if p in visited:
                continue
            visited.add(p)
            if state.point2constructions[p] not in constructions_list:
                constructions_list.append(state.point2constructions[p])
            for construction in state.point2constructions[p]:
                for dep_p in construction.inputs:
                    if dep_p not in visited:
                        queue.append(dep_p)
        return constructions_list

    proof_generator = ProofGenerator(state)
    i = 0
    for relation in state.relations:
        if isinstance(relation, (Between, SameSide, OppositeSide)):
            continue
        if isinstance(relation, Collinear) and relation.negated:
            continue
        proof_generator.run(relation)
        
        proof_generator.track_constructions(relation)
        if not isinstance(relation, (Concyclic, Collinear, Perpendicular, Parallel, Midpoint, Similar3, Congruent3)):
            continue

        points = relation.get_points()
        diagram.save_path = os.path.join(ROOT_DIR, f'samples/test{i}.jpg')
        
        if len(proof_generator.source_constructions[relation]) == 1:
            continue

        print(relation)
        for con in list(proof_generator.source_constructions[relation]):
            print(con, end=' ')
        print()
        
        diagram.draw_diagram(constructions=list(proof_generator.source_constructions[relation]), save=True)
        i += 1
        input()

        
if __name__ == '__main__':
    generate()