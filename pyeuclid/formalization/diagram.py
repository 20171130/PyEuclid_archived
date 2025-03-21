import os
import pickle

from pyeuclid.formalization.relation import *
from pyeuclid.formalization.numericals import *
from pyeuclid.formalization.utils import *


class Diagram:
    def __init__(self, constructions=None):
        self.points = []
        self.lines = []
        self.segments = []
        self.circles = []
        self.construct_diagram(constructions)
        
    def contruct_diagram(self, constructions, resample_iter=10):
        i = 0
        while i < resample_iter:
            try:
                for c in constructions:
                    self.construct_one(c)
                return
            except:
                continue
        else:
            print(f'Fails to construct a diagram for {resample_iter} iterations.')
        return
            
    def construct_one(self, construction):
        for c in construction.conditions:
            if not self.numerical_check(c):
                raise NumerialCheckFailError()
        
        
        
    def numerical_check(self, relation):
        pass
    
    def check_notcollinear(self, relation):
        
            


def sample_diagram(construction_rules, cache_folder='cache', resample_iteration=10):
    construction_rules = construction_rules.split('; ')
    for _ in range(resample_iteration):
        g, _ = gh.Graph.build_problem(problems, defs)
        if g.type2nodes[gh.Point]:
            break
        else:
            print(f"Resampling {ag_str}")

    if cache_folder is not None:
        os.makedirs(cache_folder, exist_ok=True)
        file_name = generate_md5_filename(ag_str)
        with open(f"{cache_folder}/{file_name}", 'wb') as cache_file_obj:
            pickle.dump(g, cache_file_obj)

    return g


def generate_diagram(problem, use_cache=False, output_dir='diagrams', diagram_name='sample'):
    file_name = generate_md5_filename(problem)
    if use_cache:
        
    if cache_folder is not None and os.path.exists(f"{cache_folder}/{file_name}"):
        try:
            with open(f"{cache_folder}/{file_name}", 'rb') as cache_file:
                diagram = pickle.load(cache_file)
        except Exception as e:
            diagram = sample_diagram(problem, cache_folder)
    else:
        diagram = sample_diagram(problem, cache_folder)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    nm.draw(
        g.type2nodes[gh.Point],
        g.type2nodes[gh.Line],
        g.type2nodes[gh.Circle],
        g.type2nodes[gh.Segment],
        theme = 'light',
        save_to=f"{output_dir}/"+f"{diagram_name}.jpg")
    

