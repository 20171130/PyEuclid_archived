import os
import sys
import logging

from itertools import permutations
from tqdm import tqdm

from pyeuclid.formalization.utils import *
from pyeuclid.formalization.translation import *
from pyeuclid.formalization.diagram import *
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.inference_rule import *

class State:
    def __init__(self):
        self.goal = None
        self.diagram = None
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
        
        self.set_logger(logging.DEBUG)
        
    def load_problem(self, conditions=None, goal=None, diagram=None):        
        if conditions:
            self.add_relations(conditions)
            self.categorize_variable()
        if goal:
            self.goal = goal
        if diagram:
            self.diagram = diagram
    
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
        
    def add_relations(self, relations):
        if not isinstance(relations, (tuple, list, set)):
            relations = [relations]
        for item in relations:
            if hasattr(item, "definition") and not item.negated:
                self.add_relations(item.definition())
            else:
                if isinstance(item, Relation):
                    self.add_relation(item)
                else:
                    self.add_equation(item)
    
    def add_relation(self, relation):
        if relation in self.relations:
            return
        points = relation.get_points()
        for p in points:
            self.add_point(p)
        self.relations.add(relation)
        
    def add_point(self, p):
        if not p in self.points:
            for point in self.points:
                self.lengths.add(Length(point, p))
            self.points.add(p)
    
    def add_equation(self, equation):
        # allow redundant equations for neat proofs
        equation = Traced(equation, depth=self.current_depth)
        for item in self.equations:
            if equation.expr - item.expr == 0:
                return
        points, quantities = get_points_and_symbols(equation)
        for p in points:
            self.add_point(p)
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
        
    def load_problem_from_text(self, text, diagram_path=None):
        constructions_list = get_constructions_list_from_text(text)
        goal = get_goal_from_text(text)
        
        diagram = Diagram(constructions_list, diagram_path)
        satisfied, satisfied_goal = diagram.numerical_check_goal(goal)
        
        for _ in range(MAX_DIAGRAM_ATTEMPTS):
            if satisfied:
                break
            diagram = Diagram(constructions_list, diagram_path, resample=True)
            satisfied, satisfied_goal = diagram.numerical_check_goal(goal)

        if not satisfied:
            raise Exception(f"Failed to satisfy goal after {MAX_DIAGRAM_ATTEMPTS} attempts.")
        
        self.diagram = diagram
        self.goal = satisfied_goal
        # self.diagram.show()
        
        for constructions in constructions_list:
            for construction in constructions:
                for p in construction.constructed_points():
                    self.add_point(p)
                
                relations = construction.conclusions()
                if isinstance(relations, tuple):
                    if self.diagram.numerical_check(relations[0]):
                        assert not self.diagram.numerical_check(relations[1])
                        self.add_relations(relations[0])
                    else:
                        assert self.diagram.numerical_check(relations[1])
                        self.add_relations(relations[1])
                else:
                    self.add_relations(relations)
        
        for perm in permutations(self.points, 3):
            between_relation = Between(*perm)
            if self.diagram.numerical_check(between_relation):
                self.add_relations(between_relation)
                
            notcollinear_relation = NotCollinear(*perm)
            if self.diagram.numerical_check(notcollinear_relation):
                self.add_relations(notcollinear_relation)
        
        for perm in permutations(self.points, 4):
            sameside_relation = SameSide(*perm)
            if self.diagram.numerical_check(sameside_relation):
                self.add_relations(sameside_relation)
                
            oppositeside_relation = OppositeSide(*perm)
            if self.diagram.numerical_check(oppositeside_relation):
                self.add_relations(oppositeside_relation)
    
    def simplify_equation(self, expr, depth=None):
        if depth is None:
            depth = len(self.solutions) - 1
        solved_vars = self.solutions[depth]
        expr = getattr(expr, "expr", expr)
        for symbol in expr.free_symbols:
            if symbol in solved_vars:
                value = solved_vars[symbol].expr
                expr = expr.subs(symbol, value)
        return expr
    
    def compute_ratio_and_angle_sum(self):
        dic = {}
        tmp = self.lengths.equivalence_classes()
        for x in tmp:
            for y in tmp:
                expr = self.simplify_equation(x/y)
                if not expr in dic:
                    dic[expr] = [sympy.core.mul.Mul(x, 1/y, evaluate=False)]
                else:
                    dic[expr].append(sympy.core.mul.Mul(
                        x, 1/y, evaluate=False))
        self.ratios = dic
        dic = {}
        tmp = self.angles.equivalence_classes()
        for x in tmp:
            for y in tmp:
                expr = self.simplify_equation(x+y)
                if not expr in dic:
                    dic[expr] = [x+y]
                else:
                    dic[expr].append(x+y)
        self.angle_sums = dic
        
    def solve_equation(self):
        if len(self.solutions) > self.current_depth: # have solved for this depth
            return
        raw_equations = [item for item in self.equations if not item.redundant]
        try_complex = self.try_complex
        var_types = self.var_types
        solved_vars = {}
        angle_linear, length_linear, length_ratio, others = classify_equations(raw_equations)
        for eqs, source in (angle_linear, "angle_linear"),  (length_ratio, "length_ratio"):
            free, solved = elim(eqs, var_types)
            for key, value in solved.items():
                value = Traced(value, depth=self.current_depth, sources=[source])
                value.symbol = key
                solved_vars[key] = value
        used = []
        progress = True
        exact_exhausted = False
        # prioritize on equations that contain only one variable to solve for exact values
        # then try to solve equations that are not much too complicated
        while progress:
            progress = False
            for i, eqn in enumerate(length_linear+others):
                if i in used or eqn.redundant:
                    continue
                symbols = eqn.free_symbols
                raw_eqn = eqn
                for symbol in symbols:
                    if symbol in solved_vars:
                        eqn = eqn.subs(symbol, solved_vars[symbol])
                symbols = eqn.free_symbols
                expr = process_equation(eqn.expr)
                tmp = str(expr)
                complexity = tmp.count("sin") + tmp.count("cos") + \
                    tmp.count("tan") + tmp.count("**")
                if try_complex and exact_exhausted:
                    if len(symbols) > 1 and complexity > 1:
                        continue
                else:
                    if len(symbols) > 1:
                        continue
                if len(symbols) == 0:
                    eqn.redundant = True
                    continue
                for symbol in symbols:
                    solutions = None
                    solution = None
                    pattern = re.compile(r"(cos|sin)\(\d+\*" + symbol + r"\)")
                    # sympy cannot handle solutions with +k*pi/n correctly, only one solution is returned
                    if pattern.search(tmp):
                        continue
                    try:
                        with Timeout(0.1) as tt:
                            solutions = sympy.solve(expr, symbol, domain=sympy.S.Reals)
                        # timeout when solving sin(AngleD_C_E)/20 - sin(AngleD_C_E + pi/3)/12
                        solution = process_solutions(symbol, expr, solutions, var_types)
                        # stack overflow infinite recursion when computing the real part of sqrt(2)*cos(x)/28 - cos(x + pi/4)/7
                    except:
                        # solving can fail on complicated equations
                        continue
                    if solution is None:
                        continue
                    break
                if not solution is None:
                    used.append(i)
                    progress = True
                    solution = Traced(solution, sources=eqn.sources, depth=self.current_depth)
                    solution.symbol = symbol
                    solved_vars[symbol] = solution
                    for key, value in solved_vars.items():
                        if symbol in value.free_symbols:
                            original = solved_vars[key]
                            solved_vars[key] = value.subs(symbol, solution)
                            if solved_vars[key] == 0 and 'length' in str(key).lower():
                                breakpoint()
                                assert False
                else:
                    self.logger.debug(f"abondended complex equation {eqn, raw_eqn}")
            if not progress and try_complex and not exact_exhausted:
                progress = True
                exact_exhausted = True
        self.solutions.append(solved_vars)
        # extract equivalence relations and store in union find
        dic = {}
        eqns = []
        for key, value in solved_vars.items():
            if not "Angle" in str(key) and not "Length" in str(key):
                continue
            value = value.expr
            if value in dic:
                eqns.append((dic[value], key))
            elif isinstance(value, sympy.core.symbol.Symbol) and ("Angle" in str(value) or "Length" in str(value)):
                eqns.append((key, value))
            else:
                dic[value] = key
        for eqn in eqns:
            # Remove the assertion or handle the case when unionfind is None
            unionfind = None
            if "Length" in str(eqn):
                unionfind = self.lengths
            if "Angle" in str(eqn):
                unionfind = self.angles
            if unionfind is not None:
                l, r = eqn
                unionfind.union(l, r)
    
    def get_applicable_theorems(self, theorems):
        def search_assignments(theorem):
            from z3 import Solver, BitVec, BitVecVal, ULT, And, Or
            if not theorem in self.solvers:
                self.solvers[theorem] = Solver()
            solver = self.solvers[theorem]
            solver.push()
            slots = theorem.__init__.__annotations__
            formal_entities = {}
            for key, attr_type in slots.items():
                if isinstance(attr_type, str):
                    assert attr_type == 'Point'
                else:
                    assert attr_type.__name__ == "Point"
                formal_entities[key] = Point(key)
            example = theorem(**formal_entities)
            formal_conditions = example.condition()
            import z3
            import math
            nbits = math.ceil(math.log2(len(self.points)))
            point_encoding = {}
            point_decoding = {}
            formal_points = {}
            points = list(self.points)
            points.sort(key=lambda x: x.name)
            for i, point in enumerate(points):
                point_encoding[point.name] = BitVecVal(i, nbits)
                point_decoding[BitVecVal(i, nbits)] = point
            for name in formal_entities:
                formal_points[name] = BitVec(name, nbits)
                if len(self.points) < 2**nbits:
                    solver.add(ULT(formal_points[name], len(self.points)))

            def in_component(formal, component):
                clause = False
                if len(formal) == 2:
                    for item in component:
                        actual, _ = get_points_and_symbols(item)
                        p1 = And(formal_points[formal[0]] == point_encoding[actual[0]],
                                formal_points[formal[1]] == point_encoding[actual[1]])
                        p2 = And(formal_points[formal[0]] == point_encoding[actual[1]],
                                formal_points[formal[1]] == point_encoding[actual[0]])
                        clause = Or(clause, Or(p1, p2))
                elif len(formal) == 3:
                    for item in component:
                        actual, _ = get_points_and_symbols(item)
                        p1 = And(formal_points[formal[0]] == point_encoding[actual[0]], formal_points[formal[1]]
                                == point_encoding[actual[1]], formal_points[formal[2]] == point_encoding[actual[2]])
                        p2 = And(formal_points[formal[0]] == point_encoding[actual[2]], formal_points[formal[1]]
                                == point_encoding[actual[1]], formal_points[formal[2]] == point_encoding[actual[0]])
                        clause = Or(clause, Or(p1, p2))
                else:
                    assert False
                return clause

            for cond in formal_conditions:
                clause = False
                if isinstance(cond, Relation):
                    formal = cond.get_points()
                else:
                    formal, _ = get_points_and_symbols(cond)
                if isinstance(cond, Relation):
                    if isinstance(cond, Equal):
                        clause = formal_points[cond.v1.name] == formal_points[cond.v2.name]
                        if cond.negated:
                            clause = z3.Not(clause)
                    elif isinstance(cond, Lt):
                        clause = ULT(
                            formal_points[cond.v1.name], formal_points[cond.v2.name])
                    else:
                        assert type(cond) in (
                            Collinear, SameSide, Between, Perpendicular, Concyclic, Parallel)
                        if type(cond) == Between:
                            clauses = []
                            for rel in self.relations:
                                if type(rel) == type(cond):
                                    assert not rel.negated
                                    permutations = rel.permutations()
                                    for perm in permutations:
                                        assignment = True
                                        for i in range(len(formal)):
                                            assignment = And(
                                                formal_points[formal[i]] == point_encoding[perm[i]], assignment)
                                        clauses.append(assignment)
                            clause = Or(*clauses)
                            if cond.negated:  # we have all between relations, and never store negated between relations
                                clause = z3.Not(clause)
                        else:
                            for rel in self.relations:
                                if type(rel) == type(cond) and rel.negated == cond.negated:
                                    if hasattr(rel, "permutations"):
                                        permutations = rel.permutations()
                                    else:
                                        permutations = [
                                            re.pattern.findall(str(rel))]
                                    for perm in permutations:
                                        if not isinstance(perm[0], str):
                                            perm = [item.name for item in perm]
                                        partial_assignment = True
                                        for i in range(len(formal)):
                                            partial_assignment = And(
                                                formal_points[formal[i]] == point_encoding[perm[i]], partial_assignment)
                                        clause = Or(partial_assignment, clause)
                            if type(cond) == Collinear:
                                degenerate = Or(formal_points[formal[0]]==formal_points[formal[1]], formal_points[formal[1]]==formal_points[formal[2]], formal_points[formal[2]]==formal_points[formal[0]])
                                clause = Or(clause, degenerate)
                elif isinstance(cond, sympy.core.expr.Expr):
                    pattern_eqlength = re.compile(r"^-?Length\w+ [-\+] Length\w+$")
                    pattern_eqangle = re.compile(r"^-?Angle\w+ [-\+] Angle\w+$")
                    pattern_eqratio = re.compile(
                        r"^-?Length\w+/Length\w+ [\+-] Length\w+/Length\w+$")
                    pattern_angle_const = re.compile(
                        r"^-?Angle\w+ [-\+] [\w/\d]+$")
                    pattern_angle_sum = re.compile(
                        r"^-?Angle\w+ [-\+] Angle\w+ [-\+] [\w/\d]+$")
                    s = str(cond)
                    if pattern_eqlength.match(s):
                        points, _ = get_points_and_symbols(cond)
                        l, r = points[:2], points[2:]
                        for component in self.lengths.equivalence_classes().values():
                            clause = Or(clause, And(in_component(
                                l, component), in_component(r, component)))
                    elif pattern_eqangle.match(s):
                        points, _ = get_points_and_symbols(cond)
                        l, r = points[:3], points[3:]
                        for component in self.angles.equivalence_classes().values():
                            clause = Or(clause, And(in_component(
                                l, component), in_component(r, component)))
                    elif pattern_eqratio.match(s):
                        points, _ = get_points_and_symbols(cond)
                        a, b, c, d = points[:2], points[2:4], points[4:6], points[6:8]
                        for ratios in self.ratios.values():
                            l_clause = False
                            r_clause = False
                            for ratio in ratios:
                                _, symbols = get_points_and_symbols(ratio)
                                length1, length2 = symbols
                                length1, length2 = self.lengths.find(
                                    length1), self.lengths.find(length2)
                                component1, component2 = self.lengths.equivalence_classes(
                                )[length1], self.lengths.equivalence_classes()[length2]
                                l_clause = Or(l_clause, And(in_component(
                                    a, component1), in_component(b, component2)))
                                r_clause = Or(r_clause, And(in_component(
                                    c, component1), in_component(d, component2)))
                            clause = Or(clause, And(l_clause, r_clause))
                    elif pattern_angle_const.match(s):
                        points, _ = get_points_and_symbols(cond)
                        left = points[:3]
                        cnst = [arg for arg in cond.args if len(arg.free_symbols)==0][0]
                        cnst = abs(cnst)
                        for rep, component in self.angles.equivalence_classes().items():
                            if self.check_conditions(cnst - rep):
                                clause = in_component(left, component)
                                break
                    else:
                        assert pattern_angle_sum.match(s)
                        cnst = [arg for arg in cond.args if len(
                            arg.free_symbols) == 0][0]
                        cnst = abs(cnst)
                        points, _ = get_points_and_symbols(cond)
                        left, right = points[:3], points[3:]
                        for rep, angle_sums in self.angle_sums.items():
                            if self.check_conditions(cnst-rep):
                                for angle_sum in angle_sums:
                                    if isinstance(angle_sum, sympy.core.add.Add):
                                        angle1, angle2 = angle_sum.args
                                        # angle1 + angle2
                                    else:
                                        angle1 = list(angle_sum.free_symbols)[0]
                                        angle2 = angle1
                                        # 2 * angle_1
                                    angle1, angle2 = self.angles.find(angle1), self.angles.find(angle2)
                                    try:
                                        component1, component2 = self.angles.equivalence_classes(
                                        )[angle1], self.angles.equivalence_classes()[angle2]
                                    except:
                                        breakpoint()
                                        assert False
                                    clause = Or(clause, And(in_component(
                                        left, component1), in_component(right, component2)))
                                break
                solver.add(clause)
            solutions = []
            assignments = []
            while solver.check() == z3.sat:
                m = solver.model()
                dic = {str(i): point_decoding[m[i]] for i in m}
                concrete = theorem(**dic)
                concrete._depth = self.current_depth
                # if try complex, solutions in later iterations may be weaker than previous ones and unionfind because of abondoning complex equations, causing check condition failure
                if not self.try_complex and not self.check_conditions(concrete.condition()):
                    for condition in concrete.condition():
                        if not self.check_conditions(condition):
                            print(f"Failed condition: {condition}")
                            breakpoint()
                            self.check_conditions(condition)
                            assert False
                if not concrete.degenerate():
                    assignments.append(concrete)
                solution = False
                for i in m:
                    solution = Or((formal_points[str(i)] != m[i]), solution)
                solver.add(solution)
                solutions.append(solution)
            solver.pop()
            for item in solutions:
                solver.add(item)
            solver.push()
            assignments.sort(key=lambda x: str(x))
            return assignments
        applicable_theorems = []
        pbar = tqdm(theorems, disable=self.silent)
        for theorem in pbar:
            pbar.set_description(
                f"{theorem.__name__} #rels {len(self.relations)} # eqns {len(self.equations)}")
            concrete_theorems = search_assignments(theorem)
            applicable_theorems += concrete_theorems
        return applicable_theorems
    
    def step(self, conditions, conclusions=[], outer_theorems=inference_rule_sets["basic"]):
        """
        Only considers a subset of points and conditions
        """
        assert len(conditions) > 0
        relations_bak = self.relations
        equations_bak = self.equations
        lengths_bak = self.lengths
        angles_bak = self.angles
        diagram_relations = (Between, SameSide, Collinear)
        points_bak = self.points
        try:
            self.solve_equation()
            for condition in conditions:
                if not self.check_conditions(condition):
                    raise Exception(f"Condition {condition} is not verified")
            diagram_relations = [item for item in self.relations if isinstance(item, diagram_relations)]
            self.load_problem(hypotheses=conditions)
            for relation in diagram_relations:
                if all([point in self.points for point in relation.get_points()]):
                    self.add_relation(relation)
            self.bfs(outer_theorems=outer_theorems)
            for conclusion in conclusions:
                if not self.check_conditions(conclusion):
                    raise Exception(f"Conclusion {conclusion} is not verified")
            self.points = points_bak
            self.lengths = lengths_bak
            self.angles = angles_bak
            new_relations = [item for item in self.relations if not item in conditions]
            new_equations = [item for item in self.equations if not item in conditions]
            self.relations = relations_bak
            self.equations = equations_bak
            self.add_relations(new_relations + new_equations)
            self.solutions = self.solutions[:-1]
            self.solve_equation()
        except Exception as e:
            self.points = points_bak
            self.lengths = lengths_bak
            self.angles = angles_bak
            self.relations = relations_bak
            self.equations = equations_bak
            raise e
    
    def bfs(self, inner_theorems=inference_rule_sets["ex"], outer_theorems=inference_rule_sets["basic"], depth=999999):
        def apply(inferences, silent=False):
            last = None
            cnt = 0
            for item in inferences:
                tmp = type(item)
                if not tmp == last:
                    if cnt > 3:
                        if not silent:
                            self.logger.debug(f"...and {cnt-3} more.")
                    cnt = 0
                    last = tmp
                if cnt < 3:
                    self.logger.debug(str(item))
                cnt += 1
                conclusions = item.conclusion()
                for i, conclusion in enumerate(conclusions):
                    if isinstance(conclusion, sympy.core.expr.Expr):
                        conclusion = Traced(conclusion)
                        conclusion.sources = [item]
                    else:
                        conclusion.source = item
                    conclusion.depth = self.current_depth
                    item.depth = self.current_depth
                    conclusions[i] = conclusion
                self.add_relations(conclusions)
            if cnt > 3:
                self.logger.debug(f"...and {cnt} more.")
        self.solve_equation()
        self.compute_ratio_and_angle_sum()
        for i in range(self.current_depth, self.current_depth+depth):
            self.current_depth += 1
            inner_closure = True
            while True:
                if not self.complete() is None:
                    return self.complete()
                inner_applicable = self.get_applicable_theorems(inner_theorems)
                apply(inner_applicable)
                if len(inner_applicable) == 0:
                    break
                inner_closure = False
            if not self.complete() is None:
                return self.complete()
            applicable_theorems = self.get_applicable_theorems(outer_theorems)
            apply(applicable_theorems)
            self.solve_equation()
            self.compute_ratio_and_angle_sum()
            if len(applicable_theorems) == 0 and inner_closure:
                self.logger.debug("Found Closure")
                return None
        return applicable_theorems
    
    def complete(self):
        if isinstance(self.goal, Relation):
            if self.check_conditions(self.goal):
                return True
            else:
                return None
        else:
            assert isinstance(self.goal, sympy.core.expr.Expr)
            solution = self.simplify_equation(self.goal)
            if len(solution.free_symbols) == 0:
                return solution
            return None
    
    def check_conditions(self, conditions):
        if not type(conditions) in (list, tuple, set):
            conditions = [conditions]
        conditional_relations, conditional_equations = set(), []
        i = 0
        while i < len(conditions):
            item = conditions[i]
            if isinstance(item, Equal):
                if not ((item.v1 == item.v2) ^ item.negated):
                    return False
            elif hasattr(item, "definition") and not item.negated:
                unrolled = item.definition()
                if not (isinstance(unrolled, tuple) or isinstance(unrolled, list)):
                    unrolled = unrolled,
                conditions += unrolled
            # auxillary predicate for canonical ordering of inference rule params, does not used for checking
            elif isinstance(item, Lt):
                pass
            elif isinstance(item, Between):
                if item.negated:
                    if Not(item) in self.relations:
                        return False
                else:
                    if not item in self.relations:
                        return False
                    if item.p1 == item.p2 or item.p2 == item.p3 or item.p3 == item.p1:
                        return False
            elif isinstance(item, Relation):
                if isinstance(item, Collinear) and (item.p1 == item.p2 or item.p2 == item.p3 or item.p3 == item.p1):
                    pass
                elif not item in self.relations:
                    return False
            else:
                conditional_equations.append(self.simplify_equation(item))
            i += 1
        equation_satisfied = check_equalities(conditional_equations)
        return equation_satisfied
    
    def backward(self, node, visited=set([]), depth=None, verbose=False, root=True):
        if root:
            depth = self.current_depth
            visited = set([])
        elif depth is None:
            depth = node.depth
        # self.logger.debug(f"{node}@{depth}: {getattr(node, 'sources', None)}")
        def format_proof(proof_dict, conclusion):
            proof_steps = {}
            visited = set()
            step_counter = 1

            def format_conditions(condition, proof_steps, theorem):
                s = []
                for condition in conditions:
                    if condition in proof_steps:
                        s.append(f"{condition}({proof_steps[condition][0]})")
                    else:
                        s.append(f"{condition}")
                if theorem is None:
                    return " &\n".join(s)
                return " &\n".join(s) + f"({theorem})"
            def search(node):  # root-last traversal
                nonlocal step_counter
                if node in visited or node not in proof_dict or proof_dict[node] is None:
                    return
                visited.add(node)
                conditions = proof_dict[node]
                theorem = None
                while len(conditions) == 1 and conditions[0] in proof_dict: # collapse single-condition inferences
                    if isinstance(conditions[0], InferenceRule) and not type(conditions[0]) in inference_rule_sets["ex"]:
                        theorem = conditions[0]
                    conditions = proof_dict[conditions[0]]
                for condition in conditions:
                    if condition is not None:
                        search(condition)
                if all([type(item) in (Collinear, Between, SameSide)for item in conditions]):
                    return
                if type(node) in (Traced, sympy.core.add.Add):
                    for item in visited:
                        if not item is node and type(item) in (Traced, sympy.core.add.Add):
                            if getattr(node, "expr", node) - getattr(item, "expr", item) == 0:
                                return
                            if getattr(node, "expr", node) + getattr(item, "expr", item) == 0:
                                return
                proof_steps[node] = (step_counter, conditions, theorem)
                step_counter += 1
            search(conclusion)
            print("* Proof steps:")
            lst = [(key, value) for key, value in proof_steps.items()]
            lst.sort(key=lambda x: x[1][0])
            last = -1
            for node, (step_number, conditions, theorem) in lst:
                if step_number == last:
                    continue
                last = step_number
                print(
                    f"{step_number:03}. {format_conditions(node, proof_steps, theorem)} ⇒  {node}\n")
        if node in visited:
            return {}
        if isinstance(node, InferenceRule):
            visited.add(node)
            conds = [item for item in node.condition() if type(item)
                     not in (Equal, Lt) and not item == 0]
            result = {}
            result[node] = conds
            for cond in conds:
                result.update(self.backward(cond, visited, depth=depth-1, root=False))
        elif isinstance(node, Relation):
            visited.add(node)
            if type(node) in (Between, SameSide, Lt, Equal) or type(node) == Collinear and (node.p1 == node.p2 or node.p2 == node.p3 or node.p3 == node.p1):
                return {}
            result = {}
            for tmp in self.relations:
                if tmp == node:
                    if hasattr(tmp, "source"):
                        source = tmp.source
                        result = {node: [source]}
                        result.update(self.backward(source, visited, root=False))
                    else:
                        result = {node: []}
                    break
            assert len(result) > 0, f"{node} is not proved"
        else:
            if isinstance(node, Traced):
                sources = node.sources
                if len(sources) == 0: # initial conditions
                    visited.add(node)
                elif isinstance(sources[0], str):
                    # backtrace linear systems
                    equations = [item for item in self.equations if item.depth <= node.depth]
                    if not node.symbol is None:
                        expr = node.symbol - node.expr
                    else:
                        expr = node.expr
                    conditions = find_conditions(equations, expr, sources[0])
                    if not conditions:
                        breakpoint()
                        assert False
                    sources = conditions
                else:
                    visited.add(node)
            else:
                assert isinstance(node, sympy.core.expr.Expr)
                sources = []
                solved_vars = self.solutions[min(int(depth), len(self.solutions)-1)]
                for symbol in node.free_symbols:
                    if not symbol in solved_vars:
                        continue  # free vars
                    expr = symbol-solved_vars[symbol].expr
                    expr = Traced(expr, sources=solved_vars[symbol].sources, depth=int(depth))
                    sources.append(expr)
                if isinstance(node, sympy.core.symbol.Symbol):
                    node = node - solved_vars[node].expr
            result = {node: sources}
            for item in sources:
                result.update(self.backward(item, visited, root=False))
        if root:
            format_proof(result, node)
        return result
    
    