import re
import math
import sympy

from sympy import factor_list

from pyeuclid.formalization.utils import *


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
                assert False
            else:
                return sympy.sympify(0)
        eqn = factors[0]
        for item in factors[1:]:
            eqn = eqn*item

        return eqn
    
    def process_solutions(self, var, eqn, solutions, var_types):
        symbols = eqn.free_symbols
        solutions = [item for item in solutions if len(item.free_symbols) == len(
            symbols) - 1]  # remove degenerate solutions
        if len(symbols) == 1:
            solutions = [sympy.re(sol.simplify())
                        for sol in solutions if abs(sympy.im(sol)) < 1e-3]
            try:
                if str(var).startswith("Angle"):
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

    def elim(self, equations, var_types, remove_redundant=True):        
        free_vars = []
        raw_equations = equations
        equations = [item.expr for item in equations]
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
                if remove_redundant:
                    raw_equations[i].redundant = True
                continue
            symbols = list(eqn.free_symbols)
            symbols.sort(key=lambda x: str(x))
            expr = None
            for var in symbols:
                solutions = None
                expr = None
                solutions = sympy.solve(eqn, var)
                expr = self.process_solutions(var, eqn, solutions, var_types)
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
                if remove_redundant:
                    raw_equations[i].redundant = True
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
        var_types = self.state.var_types
        solved_vars = {}
        angle_linear, length_linear, length_ratio, others = classify_equations(self.state.equations, var_types)
        for eqs, source in (angle_linear, "angle_linear"),  (length_ratio, "length_ratio"):
            free, solved = self.elim([item for item in eqs if not item.redundant], var_types)
            solved_vars.update(solved)
        free, solved = self.elim(length_linear, var_types, remove_redundant=False)
        self.state.current_depth += 0.001
        for l1, v1 in solved.items():
            if len(v1.free_symbols) == 0:
                self.state.add_conditions(Traced(l1-v1, depth=self.state.current_depth, sources=["length_linear"]))
                continue
            else:
                for l2, v2 in solved.items():
                    if len((v2/v1).free_symbols) == 0:
                        self.state.add_conditions(Traced(l1*(v2/v1)-l2, depth=self.state.current_depth, sources=["length_linear"]))

        # prioritize on equations that contain only one variable to solve for exact values
        # then try to solve equations that are not much too complicated
        for i, eqn in enumerate(others):
            if eqn.redundant:
                continue
            raw_eqn = eqn
            symbols = eqn.free_symbols
            for symbol in symbols:
                if symbol in solved_vars:
                    eqn = eqn.subs(symbol, solved_vars[symbol])
            symbols = eqn.free_symbols
            expr = self.process_equation(eqn.expr)

            angle_linear, length_linear, length_ratio, others = classify_equations([expr], var_types)
            if others:
                continue
            sources = [raw_eqn]
            for other_symbol in raw_eqn.free_symbols:
                if "angle" in str(other_symbol).lower():
                    source = "angle_linear"
                elif "length" in str(other_symbol).lower():
                    source = "length_ratio"
                else:
                    source = var_types[other_symbol]
                if not symbol == other_symbol:
                    sources.append(Traced(other_symbol - solved_vars[other_symbol], depth=self.state.current_depth, sources=[source]))
            eqn = Traced(expr, depth=self.state.current_depth, sources = sources)
            self.state.add_conditions(eqn)

        self.state.solutions = solved_vars
        
        # extract equivalence relations and store in union find
        dic = {}
        eqns = []
        for key, value in solved_vars.items():
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
        
    def compute_ratio_and_angle_sum(self):
        self.state.current_depth += 0.001
        dic = {}
        tmp = self.state.lengths.equivalence_classes()
        for component in tmp.values():
            if len(component) == 1:
                continue
            rep = self.state.simplify_equation(component[0])
            if len(rep.free_symbols)==0:
                component = component + [rep]
            for a in range(len(component)):
                for b in range(a+1, len(component)):
                    eqn = Traced(component[a]-component[b], depth=self.state.current_depth, sources=["length_ratio"], redundant=True)
                    self.state.add_conditions(eqn)

        expr2components = {}
        for x in tmp:
            for y in tmp:
                expr = self.state.simplify_equation(x/y)
                if len(expr.free_symbols) == 0 and expr != 1:
                    for a in tmp[x]:
                        for b in tmp[y]:
                            eqn = Traced(a/b-expr, depth=self.state.current_depth, sources=["length_ratio"], redundant=True)
                            self.state.add_conditions(eqn)

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
                                    eqn = Traced(a/b-c/d, depth=self.state.current_depth, sources=["length_ratio"], redundant=True)
                                    self.state.add_conditions(eqn)

        self.state.ratios = dic

        dic = {}
        tmp = self.state.angles.equivalence_classes()
        for component in tmp.values():
            if len(component) == 1:
                continue
            rep = self.state.simplify_equation(component[0])
            if len(rep.free_symbols)==0:
                component = component + [rep]
            for a in range(len(component)):
                for b in range(a+1, len(component)):
                    eqn = Traced(component[a]-component[b], depth=self.state.current_depth, sources=["angle_linear"], redundant=True)
                    self.state.add_conditions(eqn)
        
        angle_keys = list(tmp.keys())
        for i in range(len(angle_keys)):
            x = angle_keys[i]
            x_expr = self.state.simplify_equation(x)
            for j in range(i, len(angle_keys)):
                y = angle_keys[j]
                y_expr = self.state.simplify_equation(y)
                expr = self.state.simplify_equation(x+y)
                if not expr in dic:
                    dic[expr] = [x+y]
                else:
                    dic[expr].append(x+y)
                if len(expr.free_symbols) == 0 and len(x_expr.free_symbols) > 0 and len(y_expr.free_symbols) > 0:
                    component_x, component_y = tmp[x], tmp[y]
                    for a in range(len(component_x)):
                        for b in range(len(component_y)):
                            eqn = Traced(component_x[a]+component_y[b]-expr, depth=self.state.current_depth, sources=["angle_linear"], redundant=True)
                            self.state.add_conditions(eqn)
        self.state.angle_sums = dic

    def run(self):
        self.solve_equation()
        self.compute_ratio_and_angle_sum()