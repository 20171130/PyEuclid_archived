import re
import math
import sympy

from stopit import ThreadingTimeout as Timeout
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
        try:
            if is_small(eqn):
                return sympy.sympify(0)
        except:
            breakpoint()
        eqn, denominator = eqn.as_numer_denom()
        try:
            with Timeout(0.1) as tt:
                factors = factor_list(eqn)
            if is_small(factors[0]):
                return sympy.sympify(0)
            factors = factors[1]  # removes constant coefficient
            if any([item[0].is_small() for item in factors]):
                return sympy.sympify(0)
            factors = [item[0] for item in factors if not item[0].is_positive]
            if len(factors) == 0:
                if check:
                    # breakpoint()  # contradiction
                    assert False
                else:
                    return sympy.sympify(0)
            eqn = factors[0]
            for item in factors[1:]:
                eqn = eqn*item
        except:
            return eqn
        return eqn
    
    def process_solutions(self, var, eqn, solutions, var_types):
        symbols = eqn.free_symbols
        solutions = [item for item in solutions if len(item.free_symbols) == len(
            symbols) - 1]  # remove degenerate solutions
        if len(symbols) == 1:
            solutions = [sympy.re(sol.simplify())
                        for sol in solutions if abs(sympy.im(sol)) < 1e-3]
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
        if len(solutions) == 1:
            return solutions.pop()
        return None

    def elim(self, equations, var_types):        
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
            try:
                eqn = self.process_equation(eqn, check=True)
            except:
                breakpoint()
            if eqn == 0:
                raw_equations[i].redundant = True
                continue
            symbols = list(eqn.free_symbols)
            symbols.sort(key=lambda x: str(x))
            expr = None
            for var in symbols:
                solutions = None
                expr = None
                try:
                    solutions = sympy.solve(eqn, var)
                    expr = self.process_solutions(var, eqn, solutions, var_types)
                except:
                    breakpoint()
                    assert False
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
                        pass
        exprs = {key: value for key, value in exprs.items()}
        return free_vars, exprs

    
    def solve_equation(self):
        if len(self.state.solutions) > self.state.current_depth: # have solved for this depth
            return
        raw_equations = [item for item in self.state.equations if not item.redundant]
        try_complex = self.state.try_complex
        var_types = self.state.var_types
        solved_vars = {}
        angle_linear, length_linear, length_ratio, others = classify_equations(raw_equations, var_types)
        for eqs, source in (angle_linear, "angle_linear"),  (length_ratio, "length_ratio"):
            free, solved = self.elim(eqs, var_types)
            for key, value in solved.items():
                value = Traced(value, depth=self.state.current_depth, sources=[source])
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
                expr = self.process_equation(eqn.expr)
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
                    pattern = re.compile(r"(cos|sin)\(\d+\*" + str(symbol) + r"\)")
                    # sympy cannot handle solutions with +k*pi/n correctly, only one solution is returned
                    if pattern.search(tmp):
                        continue
                    try:
                        with Timeout(0.1) as tt:
                            solutions = sympy.solve(expr, symbol, domain=sympy.S.Reals)
                        # timeout when solving sin(AngleD_C_E)/20 - sin(AngleD_C_E + pi/3)/12
                        solution = self.process_solutions(symbol, expr, solutions, var_types)
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
                    solution = Traced(solution, sources=eqn.sources, depth=self.state.current_depth)
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
                    if not self.state.silent:
                        self.state.logger.debug(f"abondended complex equation {eqn, raw_eqn}")
            if not progress and try_complex and not exact_exhausted:
                progress = True
                exact_exhausted = True
        self.state.solutions.append(solved_vars)
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
                unionfind = self.state.lengths
            if "Angle" in str(eqn):
                unionfind = self.state.angles
            if unionfind is not None:
                l, r = eqn
                unionfind.union(l, r)
    
    def compute_ratio_and_angle_sum(self):
        dic = {}
        tmp = self.state.lengths.equivalence_classes()
        for x in tmp:
            for y in tmp:
                expr = self.state.simplify_equation(x/y)
                if not expr in dic:
                    dic[expr] = [sympy.core.mul.Mul(x, 1/y, evaluate=False)]
                else:
                    dic[expr].append(sympy.core.mul.Mul(
                        x, 1/y, evaluate=False))
        self.state.ratios = dic
        dic = {}
        tmp = self.state.angles.equivalence_classes()
        for x in tmp:
            for y in tmp:
                expr = self.state.simplify_equation(x+y)
                if not expr in dic:
                    dic[expr] = [x+y]
                else:
                    dic[expr].append(x+y)
        self.state.angle_sums = dic
    
    def run(self):
        self.solve_equation()
        self.compute_ratio_and_angle_sum()