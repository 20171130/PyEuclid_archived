import os
import sys
import logging
from pyeuclid.formalization.utils import *
from pyeuclid.formalization.relation import *


class State:
    def __init__(self, conditions=None, queries=None):
        self.points = set()
        self.relations = set()
        self.equations = []
        self.lengths = UnionFind()
        self.angles = UnionFind()
        self.var_types = {}
        self.ratios = {}
        self.angle_sums = {}
        
        self.current_depth = 0
        self.solutions = []
        self.solvers = {}
        self.try_complex = False
        self.silent = False
        self.logger = logging.getLogger(__name__)
        
        self.load_problem(conditions, queries)
        self.set_logger(logging.DEBUG)
        
    def load_problem(self, conditions, queries):        
        if conditions:
            self.add_relations(conditions)
            
        if queries:
            self.add_queries(queries)
            
        self.categorize_variable()
    
    def set_logger(self, level):
        self.logger.setLevel(level)
        rank = os.environ.get("OMPI_COMM_WORLD_RANK", None)
        if not len(self.logger.handlers):
            handler = logging.StreamHandler(sys.stdout)
            if rank is None:
                formatter = logging.Formatter(
                    '%(levelname)s - %(message)s')  # %(asctime)s - %(name)s -
            else:
                formatter = logging.Formatter(
                    rank+' %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def add_queries(self, queries):
        if not isinstance(queries, (tuple, list, set)):
            self.queries = [queries]
        else:
            self.queries = queries
    
    def add_relations(self, relations):
        if not isinstance(relations, (tuple, list, set)):
            relations = [relations]
        for item in relations:
            if hasattr(item, "definition") and not item.negated:
                self.add_conclusions(item.definition())
            else:
                if isinstance(item, Relation):
                    self.add_relation(item)
                else:
                    self.add_equation(item)
    
    def add_relation(self, relation):
        if relation in self.relations:
            return
        entities = relation.get_entities()
        for i in entities:
            self.add_entity(i)
        self.relations.add(relation)
        
    def add_entity(self, entity):
        if not entity in self.points:
            for point in self.points:
                self.lengths.add(Length(point, entity))
            self.points.add(entity)
    
    def add_equation(self, equation):
        # allow redundant equations for neat proofs
        equation = Traced(equation, depth=self.current_depth)
        for item in self.equations:
            if equation.expr - item.expr == 0:
                return
        entities, quantities = get_points_and_symbols(equation)
        for i in entities:
            self.add_entity(i)
        unionfind = None
        for quantity in quantities:
            if "Angle" in str(quantity):
                unionfind = self.angles
                unionfind.add(quantity)
            elif "Length" in str(quantity):
                unionfind = self.lengths
                unionfind.add(quantity)
        self.equations.append(equation)
    
    def categorize_variable(self):
        angle_linear, length_linear, length_ratio, others = classify_equations(self.equations)
        for eq in self.equations:
            if "Variable" not in str(eq):
                continue
            _, entities = get_points_and_symbols(eq)
            label = None
            if eq in angle_linear and ("Angle" in str(eq) or "pi" in str(eq)):
                label = "Angle"
            elif eq in length_linear and "Length" in str(eq):
                label = "Length"
            elif eq in length_ratio and "Length" in str(eq):
                label = "Length"
            else:
                continue
            for entity in entities:
                if label is not None:
                    if entity in self.var_types and self.var_types[entity] != label:
                        print(
                            f"Variable {entity} points to two differen entities: {label} and {self.var_types[entity]}")
                        assert False
                    else:
                        self.var_types[entity] = label
