import random

from pyeuclid.formalization.diagram import Diagram
from pyeuclid.formalization.state import State
from pyeuclid.formalization.construction_rule import *
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine


def generate_problem():
    state = State()
    state.silent = True
    deductive_database = DeductiveDatabase(state)
    algebraic_system = AlgebraicSystem(state)
    engine = Engine(state, deductive_database, algebraic_system)
    diagram = Diagram(cache_folder=None)
    state.diagram = diagram
    
    current = 0
    depth = 5
    
    while current < depth:
        constructions = []
        if current >= 1:
            candidate_set = [rule for rule in construction_rule_sets['AG'] if rule.num_inputs <= len(state.points) and rule.num_inputs > 0]
        else:
            candidate_set = [rule for rule in construction_rule_sets['AG'] if rule.num_inputs <= len(state.points)]
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
                elif picked == construct_s_segment:
                    inputs.append(random.choice(range(1, 21)))
        outputs = [Point(chr(ord('a') + num_points + i)) for i in range(picked.num_outputs)]
        construction = picked(*inputs)
        construction.construct(*outputs)
        constructions.append(construction)
        
        if current >= 1 and random.random() > 1:
            candidate_set = [rule for rule in construction_rule_sets if rule.num_inputs <= len(state.points) and rule.num_inputs > 0 and rule.num_outputs == picked.num_outputs]
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
                    elif picked == construct_s_segment:
                        inputs.append(random.choice(range(1, 21)))
            outputs = [Point(chr(ord('a') + num_points + i)) for i in range(picked.num_outputs)]
            construction = picked(*inputs)
            construction.construct(*outputs)
            constructions.append(construction)
            
        for construction in constructions:
            print(construction)
        
        try:
            diagram.add_constructions(constructions)
        except:
            continue
            
        state.add_constructions(constructions)
        # engine.search()
        current += 1
        
    diagram.show()
                
        
        
if __name__ == '__main__':
    generate_problem()