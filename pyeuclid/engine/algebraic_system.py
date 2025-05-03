import re
import math
import sympy
import random

from collections import defaultdict
from stopit import ThreadingTimeout as Timeout
from sympy import symbols, factor_list, linear_eq_to_matrix, expand_log, log, exp

from pyeuclid.formalization.utils import *



class AlgebraicSystem:
    def __init__(self, state):
        self.state = state
    
    def process_equation(self, eqn, check=False):
        if isinstance(eqn, sympy.core.add.Add):
            add_args = []
            flag = False
            for item in eqn.args:
                if isinstance(item, sympy.core.mul.Mul) and is_small(item.args[0]):
                    flag = True
                    continue
                add_args.append(item)
            if flag:
                eqn = sympy.core.add.Add(*add_args)
        if is_small(eqn):
            return sympy.sympify(0)
        eqn, denominator = eqn.as_numer_denom()
        factors = None
        try:
            with Timeout(0.1) as tt:
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
    
    # def elim1(self, equations, logarithm=False):
    #     all_vars = []
    #     traced = [eq for eq in equations if not eq.redundant]
    #     equations = [eq.expr for eq in equations if not eq.redundant]
    #     for eqn in equations:
    #         all_vars += eqn.free_symbols
    #     all_vars = list(set(all_vars))
    #     all_vars.sort(key=lambda x: x.name)
        
    #     if logarithm:
    #         log_vars = {var: symbols(f"log_{var.name}") for var in all_vars}
    #         inv_log_vars = {v: k for k, v in log_vars.items()}
    #         subs_dict = {log(v): log_vars[v] for v in all_vars}
    #         linearized_equations = []
    #         for eq in equations:
    #             log_eq = sympy.Add(*[-log(-term) if term.could_extract_minus_sign() else log(term) for term in eq.args])
    #             log_eq = expand_log(log_eq, force=True)
    #             log_eq = log_eq.subs(subs_dict)
    #             linearized_equations.append(log_eq)
            
    #         equations = linearized_equations
    #         all_vars = [log_var for log_var in log_vars.values()]
        
    #     A, b = linear_eq_to_matrix(equations, all_vars)
    #     augmented = A.row_join(b)
    #     rref_matrix, pivot_cols = augmented.rref()
    #     solved_vars = {}
    #     free_vars = []
        
    #     pivot_row_set = set(range(len(pivot_cols)))
    #     for i in range(augmented.rows):
    #         is_zero_row = all(rref_matrix[i, j] == 0 for j in range(rref_matrix.cols))
    #         is_pivot_row = i in pivot_row_set
    #         if is_zero_row or not is_pivot_row:
    #             traced[i].redundant = True

    #     for i, var in enumerate(all_vars):
    #         if i in pivot_cols:
    #             row_idx = pivot_cols.index(i)
    #             expr = -sum(rref_matrix[row_idx, j] * all_vars[j] for j in range(len(all_vars)) if j != i) + rref_matrix[row_idx, -1]
    #             solved_vars[var] = expr
    #         else:
    #             free_vars.append(var)
        
    #     if logarithm:
    #         subs_dict = {v: log(inv_log_vars[v]) for v in all_vars}
    #         final_solved = {inv_log_vars[log_var]: sympy.simplify(exp(log_expr.subs(subs_dict))) for log_var, log_expr in solved_vars.items()}
    #         final_free = [inv_log_vars[v] for v in free_vars]
            
    #         solved_vars = final_solved
    #         free_vars = final_free
        
    #     return free_vars, solved_vars

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
        # .free_symbols or .atom() are expensive, cache them isntead of compute on the fly
        eqn2symbols = [item.free_symbols for item in equations]
        # Triangulate
        for i, eqn in enumerate(equations):
            eqn = self.process_equation(eqn, check=True)
            if eqn == 0:
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
                raw_equations[i].redundant = True
                continue
            else:
                breakpoint()  # contradiction
                assert False
            if var in free_vars:
                free_vars.remove(var)
            eqns = [(idx+i+1, item) for idx,
                    item in enumerate(equations[i+1:]) if var in eqn2symbols[idx+i+1]]
            for idx, item in eqns:
                equations[idx] = item.subs(var, exprs[var])
                eqn2symbols[idx] = equations[idx].free_symbols

        expr2symbols = {key: value.free_symbols for key, value in exprs.items()}
        # Diagonalize
        for i, (key, value) in enumerate(exprs.items()):
            for j, key1 in enumerate(exprs.keys()):
                if j == i:
                    break
                if key in expr2symbols[key1]:
                    exprs[key1] = exprs[key1].subs(key, value)
                    expr2symbols[key1] = exprs[key1].free_symbols
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
            # free, solved = self.elim(eqs, logarithm=source=="length_ratio")
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
                    with Timeout(0.1) as tt:
                        solutions = sympy.solve(expr, symbol, domain=sympy.S.Reals)
                        # timeout when solving sin(AngleD_C_E)/20 - sin(AngleD_C_E + pi/3)/12
                        # stack overflow infinite recursion when computing the real part of sqrt(2)*cos(x)/28 - cos(x + pi/4)/7
                    if solutions is None:
                        # solving can fail on complicated equations
                        continue
                    solution = self.process_solutions(symbol, expr, solutions, var_types)
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
        def _compute_relations(equivalence_classes, solved_vars, value_range, operation, tol=1e-10):
            values = {}
            for var in equivalence_classes:
                if var in solved_vars:
                    expr = solved_vars[var].expr
                    for symbol in expr.free_symbols:
                        if symbol not in values:
                            values[symbol] = random.uniform(*value_range)
                    values[var] = float(expr.evalf(subs=values))
                elif var not in values:
                    values[var] = random.uniform(*value_range)

            relation_map = defaultdict(list)
            for x in equivalence_classes:
                for y in equivalence_classes:
                    if operation == "ratio":
                        v = values[x] / values[y]
                        expr = sympy.Mul(x, 1/y, evaluate=False)
                        key = round(v / tol) * tol
                        relation_map[key].append(expr)
                    elif operation == "sum":
                        v = values[x] + values[y]
                        if is_small(v-math.pi) or is_small(v-math.pi/2):
                            expr = x + y
                            key = round(v / tol) * tol
                            relation_map[key].append(expr)
            return dict(relation_map)

        lengths = list(self.state.lengths.equivalence_classes())
        angles = list(self.state.angles.equivalence_classes())
        solved_vars = self.state.solutions[-1]

        self.state.ratios = _compute_relations(lengths, solved_vars, (1.0, 10.0), operation="ratio")
        self.state.angle_sums = _compute_relations(angles, solved_vars, (1e-6, math.pi / 2), operation="sum")
        
    # def compute_ratio_and_angle_sum(self):
    #     dic = {}
    #     tmp = self.state.lengths.equivalence_classes()
    #     for x in tmp:
    #         for y in tmp:
    #             expr = self.state.simplify_equation(x/y)
    #             if not expr in dic:
    #                 dic[expr] = [sympy.core.mul.Mul(x, 1/y, evaluate=False)]
    #             else:
    #                 dic[expr].append(sympy.core.mul.Mul(
    #                     x, 1/y, evaluate=False))
    #     self.state.ratios = dic
    #     dic = {}
    #     tmp = self.state.angles.equivalence_classes()
    #     for x in tmp:
    #         for y in tmp:
    #             expr = self.state.simplify_equation(x+y)
    #             if not expr in dic:
    #                 dic[expr] = [x+y]
    #             else:
    #                 dic[expr].append(x+y)
    #     self.state.angle_sums = dic

    def run(self):
        self.solve_equation()
        self.compute_ratio_and_angle_sum()