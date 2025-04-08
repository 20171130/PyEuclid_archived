from pyeuclid.formalization.relation import *


class Engine:
    def __init__(self, state, deductive_database, algebraic_system):
        self.state = state
        self.deductive_database = deductive_database
        self.algebraic_system = algebraic_system
        
    def search(self, depth=9999):
        self.algebraic_system.run()
        for _ in range(self.state.current_depth, self.state.current_depth + depth):
            self.state.current_depth += 1
            
            if self.state.complete() is not None:
                break
            
            self.deductive_database.run()
            
            if self.deductive_database.closure:
                break
            
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
    