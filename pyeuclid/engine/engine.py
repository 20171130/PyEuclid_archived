from pyeuclid.formalization.relation import *
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebaicSystem
from pyeuclid.engine.proof_generator import ProofGenerator


class Engine:
    def __init__(self, state):
        self.state = state
        self.deductive_database = DeductiveDatabase(state)
        self.algebraic_system = AlgebaicSystem(state)
        self.proof_generator = ProofGenerator(state)
        
    def search(self, depth=9999):
        self.algebraic_system.run()
        for _ in range(self.state.current_depth, self.state.current_depth + depth):
            self.state.current_depth += 1
            
            if self.state.complete() is not None:
                break
            
            self.deductive_database.run()
            
            if self.state.complete() is not None:
                break
            
            self.algebraic_system.run()
    
    def step(self, conditions, conclusions=[]):
        """
        Only considers a subset of points and conditions
        """
        assert len(conditions) > 0
        relations_bak = self.state.relations
        equations_bak = self.state.equations
        lengths_bak = self.state.lengths
        angles_bak = self.state.angles
        points_bak = self.state.points
        
        diagrammatic_relations = (Between, SameSide, Collinear)
        
        try:
            self.algebraic_system.solve_equation()
            for condition in conditions:
                if not self.state.check_conditions(condition):
                    raise Exception(f"Condition {condition} is not verified")
            diagrammatic_relations = [item for item in self.state.relations if isinstance(item, diagrammatic_relations)]
            
            self.state.add_relations(conditions)

            for relation in diagrammatic_relations:
                if all([point in self.points for point in relation.get_points()]):
                    self.state.add_relation(relation)
                
            self.deductive_database.run()
            
            for conclusion in conclusions:
                if not self.state.check_conditions(conclusion):
                    raise Exception(f"Conclusion {conclusion} is not verified")
                
            self.state.points = points_bak
            self.state.lengths = lengths_bak
            self.state.angles = angles_bak
            new_relations = [item for item in self.state.relations if not item in conditions]
            new_equations = [item for item in self.state.equations if not item in conditions]
            self.state.relations = relations_bak
            self.state.equations = equations_bak
            self.state.add_relations(new_relations + new_equations)
            self.state.solutions = self.state.solutions[:-1]
            self.algebraic_system.solve_equation()
        
        except Exception as e:
            self.state.points = points_bak
            self.state.lengths = lengths_bak
            self.state.angles = angles_bak
            self.state.relations = relations_bak
            self.state.equations = equations_bak
            raise e
    
    
    def proof_generartion(self):
        self.proof_generator.run(self.state.goal)