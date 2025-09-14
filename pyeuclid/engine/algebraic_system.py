import re
import math
import sympy

from sympy import factor_list
from itertools import combinations
from tqdm import tqdm
from pyeuclid.formalization.utils import *
from stopit import ThreadingTimeout as TT, SignalTimeout as ST

remove_redundant = True

class AlgebraicSystem:
    def __init__(self, state):
        self.state = state
    
    def process_equation(self, eqn, check=False):
        if isinstance(eqn, sympy.core.add.Add):
            add_args = []
            for item in eqn.args:
                if isinstance(item, sympy.core.mul.Mul) and is_small(item.args[0]):
                    continue
                add_args.append(item)
            eqn = sympy.core.add.Add(*add_args)
        if is_small(eqn):
            return sympy.sympify(0)
        eqn, denominator = eqn.as_numer_denom()
        factors = None
        try:
            with Timeout(0.1):
                factors = factor_list(eqn)
        except:
            pass
        if factors is None:
            return eqn
        if is_small(factors[0]):
            return sympy.sympify(0)
        factors = factors[1]  # removes constant coefficient
        if any([is_small(item[0]) for item in factors]):
            return sympy.sympify(0)
        factors = [item[0] for item in factors if not item[0].is_positive]
        if len(factors) == 0:
            if check:
                breakpoint()
                assert False
            else:
                return sympy.sympify(0)
        eqn = factors[0]
        for item in factors[1:]:
            eqn = eqn*item
        return eqn.expand()
    
    def process_solutions(self, var, eqn, solutions, var_types):
        def _all_terms_have_factor(expr: sympy.Expr, sym: sympy.Symbol) -> bool:
            num, den = expr.as_numer_denom()
            num = sympy.expand(num)

            if num == 0:
                return False

            if isinstance(num, sympy.Add):
                terms = num.as_ordered_terms()
            else:
                terms = [num]

            for t in terms:
                pd = t.as_powers_dict()
                if pd.get(sym, 0) < 1:
                    return False
            return True
        
        symbols = eqn.free_symbols
        solutions = [item for item in solutions if len(item.free_symbols) == len(
            symbols) - 1 and not item.has(sympy.nan, sympy.zoo, sympy.oo, -sympy.oo)]  # remove degenerate solutions
        
        if sympy.Integer(0) in solutions and len(eqn.free_symbols) > 1 and _all_terms_have_factor(eqn, var):
            solutions = [s for s in solutions if s != 0]
        
        if len(symbols) == 1:
            solutions = [sympy.re(sol.simplify())
                        for sol in solutions if abs(sympy.im(sol)) < 1e-3]
            try:
                if str(var).startswith("Angle"):
                    solutions = {j%(2*math.pi) for j in solutions}
                    solutions = {j for j in solutions if j >= 0 and j <= math.pi+eps}
                    # Prioitize non-zero and non-flat angle
                    if len(solutions) > 1:
                        solutions = {j for j in solutions if j != 0 and j != sympy.pi}
                elif var_types.get(var, None) == "Angle":
                    solutions = {j for j in solutions if j >=
                                0 and j <= 180+eps/math.pi*180}
                    # Prioitize non-zero and non-flat angle
                    if len(solutions) > 1:
                        solutions = {j for j in solutions if j != 0 and j != 180}
                if len(solutions) > 1:
                    solutions = [item for item in solutions if item >= 0]
                if len(solutions) > 1:
                    solutions = [item for item in solutions if item > 0]
            except:
                if str(var).startswith("Angle"):
                    solutions = {j for j in solutions if float(j) >= 0 and float(j) <= math.pi+eps}
                    # Prioitize non-zero and non-flat angle
                    if len(solutions) > 1:
                        solutions = {j for j in solutions if float(j) != 0 and float(j) != sympy.pi}
                elif var_types.get(var, None) == "Angle":
                    solutions = {j for j in solutions if j >=
                                0 and j <= 180+eps/math.pi*180}
                    # Prioitize non-zero and non-flat angle
                    if len(solutions) > 1:
                        solutions = {j for j in solutions if float(j) != 0 and float(j) != 180}
                if len(solutions) > 1:
                    solutions = [item for item in solutions if float(item) >= 0]
                if len(solutions) > 1:
                    solutions = [item for item in solutions if float(item) > 0]
                    
        if len(solutions) == 1:
            return solutions.pop()
        return None

    def elim(self, eq_type, equations, var_types):
        if remove_redundant:    
            raw_equations = [eq for eq in equations if eq_type not in eq.redundant]
        else:
            raw_equations = equations
        equations = [item.expr for item in raw_equations]
        free_vars = []
        for eqn in equations:
            free_vars += eqn.free_symbols
        free_vars = set(free_vars)
        free_vars = list(free_vars)
        free_vars.sort(key=lambda x: x.name)
        exprs = {}
        # Triangulate
        for i, eqn in enumerate(equations):
            eqn = self.process_equation(eqn, check=True)
            if eqn == 0:
                raw_equations[i].redundant.add(eq_type)
                continue
            symbols = list(eqn.free_symbols)
            symbols.sort(key=lambda x: str(x))
            expr = None
            for var in symbols:
                solutions = None
                expr = None
                solutions = sympy.solve(eqn, var)
                expr = self.process_solutions(var, eqn, solutions, var_types)
                if expr == 0:
                    breakpoint()
                if expr is None:
                    continue
                else:
                    break
            if expr is None:
                continue
            if expr == 0 and "length" in str(var).lower():
                breakpoint()
                assert False
            if expr == 0 and "radius" in str(var).lower():
                breakpoint()
                assert False
            if not var in exprs:
                exprs[var] = expr
            elif check_equalities(expr-exprs[var]):  # redundant equation
                equations[i] = sympy.sympify(0)
                raw_equations[i].redundant.add(eq_type)
                continue
            else:
                breakpoint()  # contradiction
                assert False
            if var in free_vars:
                free_vars.remove(var)
            eqns = [(idx+i+1, item) for idx,
                    item in enumerate(equations[i+1:]) if var in item.free_symbols]
            for idx, item in eqns:
                if var in getattr(equations[idx], "free_symbols", []):
                    equations[idx] = item.subs(var, exprs[var])
        # Diagonalize
        for i, (key, value) in enumerate(exprs.items()):
            for j, key1 in enumerate(exprs.keys()):
                if j == i:
                    break
                if key in getattr(exprs[key1], "free_symbols", []):
                    old = exprs[key1]
                    exprs[key1] = exprs[key1].subs(key, value)
                    if str(exprs[key1]) == "0" and "Length" in str(key1):
                        breakpoint()
                        assert False
        exprs = {key: value for key, value in exprs.items()}
        return free_vars, exprs

    def solve_equation(self):
        closure = True
        var_types = self.state.var_types
        angle_linear, length_linear, length_ratio, others = classify_equations(self.state.equations, var_types)        
        angle_linear_free, angle_linear_solved = self.elim('angle_linear', angle_linear, var_types)
        length_ratio_free, length_ratio_solved = self.elim('length_ratio', length_ratio, var_types)
        length_linear_free, length_linear_solved = self.elim('length_linear',length_linear, var_types)

        self.state.solutions['angle_linear'] = angle_linear_solved
        self.state.solutions['length_ratio'] = length_ratio_solved
        self.state.solutions['length_linear'] = length_linear_solved

        # extract equivalence relations and store in union find
        dic = {}
        eqns = []
        for key, value in (length_ratio_solved | angle_linear_solved).items():
            if not "Angle" in str(key) and not "Length" in str(key):
                continue
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
                unionfind = self.state.lengths
            if "Angle" in str(eqn):
                unionfind = self.state.angles
            if unionfind is not None:
                l, r = eqn
                unionfind.union(l, r)
        
        self.state.current_depth += 1
        self.compute_ratio_and_angle_sum()

        for l1, v1 in length_linear_solved.items():
            if len(v1.free_symbols) == 0:
                eqn = Traced(l1-v1, depth=self.state.current_depth, sources=["length_linear"])
                self.state.add_conditions(eqn)
                continue
            else:
                for l2, v2 in length_linear_solved.items():
                    if len((v2/v1).free_symbols) == 0:
                        eqn = Traced(l1*(v2/v1)-l2, depth=self.state.current_depth, sources=["length_linear"])
                        self.state.add_conditions(eqn)
        
        self.state.current_depth += 1

        for original_solved, substitute_solved in [(length_ratio_solved, length_linear_solved), (length_linear_solved, length_ratio_solved)]:
            for key, value in original_solved.items():
                eqn = key - value
                raw_eqn = eqn
                sources = [raw_eqn]
                eqn = self.state.simplify_equation(eqn, substitute_solved)
                if self.state.simplify_equation(eqn, original_solved) == 0:
                    continue
                symbols = [symbol for symbol in raw_eqn.free_symbols if symbol in substitute_solved]
                for symbol in symbols:
                    sources.append(symbol - substitute_solved[symbol])
                expr = self.process_equation(eqn)
                s = str(expr)
                complexity = s.count("sin") + s.count("cos") + s.count("tan") + s.count("**")/2
                if complexity > 2:
                    continue
                if len(expr.free_symbols) > 0:
                    if len(expr.free_symbols) <= 2:
                        symbol = list(expr.free_symbols)[0]
                        solutions = []
                        try:
                            with ST(1):
                                with TT(0.1):
                                    solutions = sympy.solve(expr, symbol)
                        except:
                            continue
                        solution = self.process_solutions(symbol, expr, solutions, var_types)
                        if solution is None:
                            continue
                        expr = symbol - solution
                    traced = Traced(expr)
                    kinds = classify_equations([traced], var_types)
                    if kinds[-1]:
                        continue
                    eqn = Traced(expr, depth=self.state.current_depth, sources=sources)
                    if eqn not in self.state.equations:
                        self.state.add_conditions(eqn)
                        closure = False

        # prioritize on equations that contain only one variable to solve for exact values
        # then try to solve equations that are not much too complicated
        for i, length_solved in enumerate([length_ratio_solved, length_linear_solved]):
            solved = angle_linear_solved | length_solved
            pbar = others if self.state.silent else tqdm(others)
            for eqn in pbar:
                if len(self.state.simplify_equation(eqn, solved).free_symbols) == 0:
                    eqn.redundant.add('others')
                    continue
                if 'others' in eqn.redundant and remove_redundant:
                    continue
                raw_eqn = eqn
                symbols = [symbol for symbol in raw_eqn.free_symbols if symbol in solved]
                symbol2sources = {}
                for symbol in symbols:
                    symbol2sources[symbol] = symbol - solved[symbol]
                eqn = raw_eqn
                sources = [raw_eqn]
                for symbol in symbols:
                    try:
                        with TT(0.1):
                            eqn = eqn.subs(symbol, solved[symbol])
                    except:
                        continue
                    sources.append(symbol2sources[symbol])
                expr = self.process_equation(eqn.expr)
                if len(expr.free_symbols) > 0:
                    if len(expr.free_symbols) <= 2:
                        symbol = list(expr.free_symbols)[0]
                        solutions = []
                        try:
                            with TT(0.1):
                                solutions = sympy.solve(expr, symbol)
                        except:
                            continue
                        solution = self.process_solutions(symbol, expr, solutions, var_types)
                        if solution is None:
                            continue
                        expr = symbol - solution
                    traced = Traced(expr)
                    kinds = classify_equations([traced], var_types)
                    if kinds[-1]:
                        continue
                    eqn = Traced(expr, depth=self.state.current_depth, sources=sources)
                    if eqn not in self.state.equations:
                        self.state.add_conditions(eqn)
                        closure = False
        
        return closure
        
    def compute_ratio_and_angle_sum(self):
        dic = {}
        tmp = self.state.lengths.equivalence_classes()
        for component in tmp.values():
            if len(component) == 1:
                continue
            rep = self.state.simplify_equation(component[0], self.state.solutions['length_ratio'])
            if len(rep.free_symbols)==0:
                component = component + [rep]
            for a in range(len(component)):
                for b in range(a+1, len(component)):
                    eqn = Traced(component[a]-component[b], depth=self.state.current_depth, sources=["length_ratio"], redundant={"length_ratio"})
                    self.state.add_conditions(eqn)

        expr2components = {}
        for x in tmp:
            for y in tmp:
                expr = self.state.simplify_equation(x/y,  self.state.solutions['length_ratio'])
                if len(expr.free_symbols) == 0 and expr != 1:
                    for a in tmp[x]:
                        for b in tmp[y]:
                            eqn = Traced(a/b-expr, depth=self.state.current_depth, sources=["length_ratio"], redundant={"length_ratio"})
                            self.state.add_conditions(eqn)
                            eqn1 = Traced(a-expr*b, depth=self.state.current_depth, sources=["length_ratio"], redundant={"length_ratio"})
                            self.state.add_conditions(eqn1)

                if not expr in dic:
                    dic[expr] = [sympy.core.mul.Mul(x, 1/y, evaluate=False)]
                    if len(expr.free_symbols) > 0:
                        expr2components[expr] = [(x, y)]
                else:
                    dic[expr].append(sympy.core.mul.Mul(
                        x, 1/y, evaluate=False))
                    if len(expr.free_symbols) > 0:
                        expr2components[expr].append((x, y))
                    
        for expr, components in expr2components.items():
            for i in range(len(components)):
                for j in range(i+1, len(components)):
                    x1, y1 = components[i]
                    x2, y2 = components[j]
                    for a in tmp[x1]:
                        for b in tmp[y1]:
                            for c in tmp[x2]:
                                for d in tmp[y2]:
                                    eqn = Traced(a/b-c/d, depth=self.state.current_depth, sources=["length_ratio"], redundant={"length_ratio"})
                                    self.state.add_conditions(eqn)

        self.state.ratios = dic

        dic = {}
        tmp = self.state.angles.equivalence_classes()
        for component in tmp.values():
            if len(component) == 1:
                continue
            rep = self.state.simplify_equation(component[0], self.state.solutions['angle_linear'])
            if len(rep.free_symbols)==0:
                component = component + [rep]
            for a in range(len(component)):
                for b in range(a+1, len(component)):
                    eqn = Traced(component[a]-component[b], depth=self.state.current_depth, sources=["angle_linear"], redundant={"angle_linear"})
                    self.state.add_conditions(eqn)
        
        angle_keys = list(tmp.keys())
        for i in range(len(angle_keys)):
            x = angle_keys[i]
            x_expr = self.state.simplify_equation(x, self.state.solutions['angle_linear'])
            for j in range(i, len(angle_keys)):
                y = angle_keys[j]
                y_expr = self.state.simplify_equation(y, self.state.solutions['angle_linear'])
                expr = self.state.simplify_equation(x+y, self.state.solutions['angle_linear'])
                if not expr in dic:
                    dic[expr] = [x+y]
                else:
                    dic[expr].append(x+y)
                if len(expr.free_symbols) == 0 and len(x_expr.free_symbols) > 0 and len(y_expr.free_symbols) > 0:
                    component_x, component_y = tmp[x], tmp[y]
                    for a in range(len(component_x)):
                        for b in range(len(component_y)):
                            eqn = Traced(component_x[a]+component_y[b]-expr, depth=self.state.current_depth, sources=["angle_linear"], redundant={"angle_linear"})
                            self.state.add_conditions(eqn)
        self.state.angle_sums = dic

    def run(self):
        return self.solve_equation()