import math
import numpy as np
import sympy

from sympy.printing.str import StrPrinter

from pyscipopt import Model, quicksum
from collections import defaultdict

from pyeuclid.formalization.relation import *
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.utils import *
from pyeuclid.engine.inference_rule import *


class CustomPrinter(StrPrinter):
    """
    Clean, recursion-safe SymPy string printer:
    - Eq: moves negative numeric terms to RHS and flips the numeric sign
          (e.g., X*(-1/2) on LHS -> (1/2)*X on RHS).
    - Add: tidy '+/-' joins; single leading '-'.
    - Mul: no '1*...' or '-1*...'; single leading '-'; avoids recursion loops.
    - Pow: parenthesizes negative exponents.
    """

    # ---------- Equality: canonical split by numeric sign ----------
    def _print_Equality(self, expr):
        # Consolidate to one side, then send negative-numeric terms to RHS with flipped sign
        consolidated = expr.lhs - expr.rhs
        lhs_terms, rhs_terms = [], []

        for term in sympy.Add.make_args(consolidated):
            coeff, rest = term.as_coeff_Mul()  # (-1/2, Length_C_D) for Length_C_D*(-1/2)
            # If there's a numeric coeff and it's negative, flip and move to RHS
            if coeff.is_number and getattr(coeff, "is_negative", False):
                rhs_terms.append((-coeff) * rest)   # e.g., (1/2)*Length_C_D
            else:
                lhs_terms.append(term)

        new_lhs = sympy.Add(*lhs_terms) if lhs_terms else sympy.S.Zero
        new_rhs = sympy.Add(*rhs_terms) if rhs_terms else sympy.S.Zero
        return f"{self._print(new_lhs)} = {self._print(new_rhs)}"

    # ---------- Add: clean '+/-' joins ----------
    def _print_Add(self, expr, order=None):
        if hasattr(self, "_as_ordered_terms"):
            terms = self._as_ordered_terms(expr, order=order)
        else:
            terms = list(sympy.Add.make_args(expr))
        if not terms:
            return "0"

        out = []
        for i, term in enumerate(terms):
            if self._term_is_negative(term):
                piece = self._print(-term)
                out.append(f"-{piece}" if i == 0 else f" - {piece}")
            else:
                piece = self._print(term)
                out.append(piece if i == 0 else f" + {piece}")
        return "".join(out)

    # ---------- Mul: strip ±1 and avoid recursion ----------
    def _print_Mul(self, expr, order=None):
        coeff, rest = expr.as_coeff_Mul()  # (1, expr) if no numeric coeff

        # Avoid infinite recursion when no numeric coeff was extracted
        if coeff == 1:
            return super()._print_Mul(expr)

        if coeff == -1:
            return "-" + self._print(rest)

        if rest == 1:
            return self._print(coeff)

        if getattr(coeff, "is_negative", False):
            # Single leading minus; flip coeff to positive
            return "-" + f"{self._print(-coeff)}*{self._print(rest)}"

        return f"{self._print(coeff)}*{self._print(rest)}"

    # ---------- Pow: parenthesize negative exponents ----------
    def _print_Pow(self, expr):
        base, exp = expr.as_base_exp()
        if getattr(exp, "is_negative", False):
            return f"{self._print(base)}**({self._print(exp)})"
        return super()._print_Pow(expr)

    # ---------- Helper ----------
    def _term_is_negative(self, term):
        """True if additive term has an overall negative numeric coefficient."""
        coeff, _ = term.as_coeff_Mul()
        if getattr(coeff, "is_negative", None):
            return True
        # Fallback: catch x*(-2) patterns if needed
        if term.is_Mul and any(getattr(a, "is_negative", False) for a in term.args if a.is_number):
            return True
        return bool(getattr(term, "is_negative", False))


def pretty_print_expr(expr):
    """Formats any SymPy expression using the CustomPrinter."""
    return str(expr)
    # return CustomPrinter().doprint(sympy.Eq(expr, 0))


class ProofGenerator:
    def __init__(self, state, norm=1, max_equation_length_perstep=6):
        self.state = state
        self.norm = norm
        self.max_equation_length_perstep = max_equation_length_perstep

        self.visited = set()
        self.proof_dict = {}
        self.cache_conditions = {}
        self.cache_source = {}
        self.source_constructions = defaultdict(list)
    
    def run(self, node=None, depth=None, root=True):
        if isinstance(node, ConstructionRule):
            return [node]
        
        if root or depth is None:
            depth = self.state.current_depth
        
        depth = min(getattr(node, "depth", self.state.current_depth), depth)
            
        if not node and self.state.goal:
            node = self.state.goal
            if not self.state.complete() is True:
                node = node - self.state.complete()
                
        if isinstance(node, Traced):
            if node.expr in self.visited:
                return self.source_constructions[node.expr]
            else:
                self.visited.add(node.expr)
        else:
            if node in self.visited:
                return self.source_constructions[node]
            else:
                self.visited.add(node)
                
        if isinstance(node, sympy.core.expr.Expr):
            terms = node.as_ordered_terms()
            if isinstance(terms[0], sympy.core.mul.Mul) and terms[0].args[0].is_constant():
                node = node/terms[0].args[0]
            
            for item in self.state.equations:
                if item.depth < depth:
                    if item.expr == node:
                        node = item
                        depth = item.depth
                        break

        constructions = set()
        
        if isinstance(node, InferenceRule):
            conditions = [item for item in node.condition() if not trivial_condition(item)]
            self.proof_dict[node] = conditions
            for cond in conditions:
                cond_constructions = self.run(cond, depth=depth, root=False)
                constructions.update(cond_constructions)
            self.source_constructions[node] = sorted(constructions, key=lambda c: self.state.construction2index[c])
            return self.source_constructions[node]

        elif isinstance(node, Relation):
            for tmp in self.state.relations:
                if tmp == node:
                    if hasattr(tmp, "source"):
                        source = tmp.source
                        self.proof_dict[node] = [source]
                        cond_constructions = self.run(source, depth=depth, root=False)
                        constructions.update(cond_constructions)
                        self.source_constructions[node] = sorted(constructions, key=lambda c: self.state.construction2index[c])
                        return self.source_constructions[node]
                    else:
                        self.proof_dict[node] = []
                        return []
            else:
                assert False, f"{node} is not proved"
        else:
            if isinstance(node, Traced):
                sources = node.sources
                expr = node.expr
                if len(sources) == 0:
                    self.proof_dict[expr] = []
                    return []
                if isinstance(sources[0], str):
                    # backtrace linear systems
                    equations = [item for item in self.state.equations if item.depth < node.depth]
                    if expr in self.cache_conditions:
                        conditions = self.cache_conditions[expr]
                    else:
                        conditions = self.find_conditions(equations, expr, sources[0])
                    
                    if self.max_equation_length_perstep:
                        discards = []
                        while len(conditions) > self.max_equation_length_perstep:
                            additional_equations = []
                            candidate_intermediate_conditions = [item for item in self.state.equations if item.depth == node.depth and item not in equations and item not in discards]

                            for intermediate_condition in candidate_intermediate_conditions:
                                if intermediate_condition.expr in self.cache_conditions:
                                    if self.cache_source[intermediate_condition.expr] == sources[0]:
                                        cond = self.cache_conditions[intermediate_condition.expr]
                                    else:
                                        cond = None
                                else:
                                    cond = self.find_conditions(equations, intermediate_condition.expr, sources[0])
                                
                                if cond:
                                    if len(cond) <= self.max_equation_length_perstep:
                                        self.cache_conditions[intermediate_condition.expr] = cond
                                        self.cache_source[intermediate_condition.expr] = sources[0]
                                        additional_equations.append(intermediate_condition)
                                else:
                                    discards.append(intermediate_condition)
                            
                            if len(additional_equations) == 0:
                                break
                            
                            equations = equations+additional_equations
                            conditions = self.find_conditions(equations, expr, sources[0])
                    
                    self.cache_conditions[expr] = conditions
                    self.cache_source[expr] = sources[0]
                    sources = conditions
                else:
                    # sources annotated, from inference rules or solve complex
                    pass
                self.proof_dict[expr] = sources
                if not sources:
                    breakpoint()
                for item in sources:
                    cond_constructions = self.run(item, depth=depth, root=False)
                    constructions.update(cond_constructions)
                self.source_constructions[expr] = sorted(constructions, key=lambda c: self.state.construction2index[c])
                return self.source_constructions[expr]
            else:
                assert isinstance(node, sympy.core.expr.Expr)
                source = None
                equations = [item for item in self.state.equations if item.depth < depth]
                if node in self.cache_conditions:
                    conditions = self.cache_conditions[node]
                    source = self.cache_source[node]
                else:
                    for source in ("angle_linear", "length_ratio", "length_linear"):
                        conditions = self.find_conditions(equations, node, source)
                        if conditions:
                            break

                # for goals are not log linear or linear
                if conditions is None:
                    conditions = []
                    expr = node
                    for length_solved in [self.state.solutions['length_ratio'], self.state.solutions['length_linear']]:
                        solutions = self.state.solutions['angle_linear'] | length_solved
                        if self.state.simplify_equation(expr, solutions) == 0:
                            symbols = [symbol for symbol in node.free_symbols if symbol in solutions]
                            for symbol in symbols:
                                conditions.append(symbol - solutions[symbol])
                            break
                
                if self.max_equation_length_perstep:
                    discards = []
                    while len(conditions) > self.max_equation_length_perstep:
                        additional_equations = []
                        candidate_intermediate_conditions = [item for item in self.state.equations if item.depth == depth and item not in equations and item not in discards]

                        for intermediate_condition in candidate_intermediate_conditions:
                            if intermediate_condition.expr in self.cache_conditions:
                                if self.cache_source[intermediate_condition.expr] == source:
                                    cond = self.cache_conditions[intermediate_condition.expr]
                                else:
                                    cond = None
                            else:
                                cond = self.find_conditions(equations, intermediate_condition.expr, source)
                            
                            if cond:
                                if len(cond) <= self.max_equation_length_perstep:
                                    self.cache_conditions[intermediate_condition.expr] = cond
                                    self.cache_source[intermediate_condition.expr] = source
                                    additional_equations.append(intermediate_condition)
                            else:
                                discards.append(intermediate_condition)
                        
                        if len(additional_equations) == 0:
                            break
                        
                        equations = equations + additional_equations
                        conditions = self.find_conditions(equations, node, source)

                self.cache_conditions[node] = conditions
                self.cache_source[node] = source
                sources = conditions
                self.proof_dict[node] = sources
                if sources is None:
                    breakpoint()
                for item in sources:
                    cond_constructions = self.run(item, root=False, depth=depth)
                    constructions.update(cond_constructions)
                
                self.source_constructions[node] = sorted(constructions, key=lambda c: self.state.construction2index[c])
                return self.source_constructions[node]
        

    def format_proof(self, conclusion=None):
        proof = []
        proof_steps = {}
        visited = set()
        step_counter = 1

        if not conclusion and self.state.goal:
            conclusion = self.state.goal

        def format(node):
            nonlocal step_counter
            shape_dependency = {
                Trapezoid: [PropertyOfParallelogram, PropertyOfRhombus, PropertyOfRectangle, PropertyOfSquare],
                Kite: [PropertyOfRhombus, PropertyOfSquare],
                Parallelogram: [PropertyOfRhombus, PropertyOfRectangle, PropertyOfSquare],
                Rhombus: [PropertyOfSquare],
                Rectangle: [PropertyOfSquare],
            }

            def trace_fundamental_shape(node):
                theorem = None
                while (
                    isinstance(node, tuple(shape_dependency.keys())) and
                    (conditions := self.proof_dict[node]) and
                    len(conditions) == 1 and
                    isinstance(conditions[0], InferenceRule) and
                    isinstance(conditions[0], tuple(shape_dependency[type(node)]))
                ):
                    theorem = conditions[0]
                    node = theorem.condition()[0]
                return node, theorem
            
            if isinstance(node, Traced):
                if node.expr in visited:
                    return
                else:
                    visited.add(node.expr)
                    node = node.expr
            elif isinstance(node, sympy.core.expr.Expr):
                terms = node.as_ordered_terms()
                if isinstance(terms[0], sympy.core.mul.Mul) and terms[0].args[0].is_constant():
                    node = node/terms[0].args[0]
                if node in visited:
                    return
                else:
                    visited.add(node)
            else:
                if node in visited or node not in self.proof_dict: # diagrammatic relations
                    return
                visited.add(node)
            
            if node not in self.proof_dict:
                breakpoint()
            
            conditions = self.proof_dict[node]
            
            theorem = None

            # Handle inference rules
            if len(conditions) == 1 and isinstance(conditions[0], InferenceRule):
                theorem = conditions[0]
                conditions = self.proof_dict[conditions[0]]
            
            # Skip trivial conditions
            # if type(theorem) in (DiagramAngle4a, DiagramAngle4b, DiagramAngle2, FlatAngle, FlatAngle2):
            #     return

            # Trace fundamental shape
            if len(conditions) == 1 and type(conditions[0]) in shape_dependency:
                condition, theorem = trace_fundamental_shape(conditions[0])
                conditions = [condition]
            
            for condition in conditions:
                format(condition)
            
            # Skip if all conditions are basic geometric relations
            # if all([type(item) in (Collinear, Between, SameSide) for item in conditions]):
            #     return
            
            proof_steps[node] = (step_counter, conditions, theorem)
            step_counter += 1

        format(conclusion)

        merged_steps = {}
        for node, (step_number, conditions, theorem) in proof_steps.items():
            key = tuple(sorted([str(c) for c in conditions]))
            if key not in merged_steps:
                merged_steps[key] = {
                    'step_number': step_number,
                    'conditions': conditions,
                    'theorem': theorem,
                    'conclusions': []
                }
            merged_steps[key]['conclusions'].append(node)
            merged_steps[key]['step_number'] = min(merged_steps[key]['step_number'], step_number)

        # Convert grouped steps back to proof format
        sorted_steps = sorted(merged_steps.values(), key=lambda x: x['step_number'])
        
        for step in sorted_steps:
            proof.append({
                'conditions': step['conditions'],
                'theorem': step['theorem'],
                'conclusions': step['conclusions']
            })
        
        return proof
    
    def show_proof(self, node=None, verbose=False, angle="radian"):
        res = self.get_proof_str(node, verbose, angle=angle)
        print(res)

    def get_proof_str(self, node=None, verbose=False, angle="radian"):
        res = "Solution:\n"
        proof = self.get_proof(node)
        def _format(items):
            formatted_items = []
            for item in items:
                if isinstance(item, Traced):
                    item = item.expr
                if isinstance(item, sympy.core.expr.Expr):
                    if angle == "degree":
                        item = item.subs(pi, 180)
                    s = pretty_print_expr(item)
                else:
                    s = str(item)
                formatted_items.append(s)
            return ' & '.join(formatted_items)

        for step, (conditions, theorem, conclusions) in enumerate(proof):
            theorem_str = ""
            res += f"{step + 1}. {_format(conditions)}{theorem_str} => {_format(conclusions)}\n"
        return res
    
    def get_proof(self, node=None):
        res = []
        if not node and self.state.goal:
            node = self.state.goal
            if not (self.state.complete() == 0 or self.state.complete() is True):
                node = node - self.state.complete()
        
        proof_steps = self.format_proof(node)

        for proof_step in proof_steps:
            if proof_step['conditions'] and not isinstance(proof_step['conditions'][0], ConstructionRule):
                res.append((
                    [item for item in proof_step['conditions'] if not trivial_condition(item)], 
                    proof_step['theorem'], 
                    proof_step['conclusions']
                ))
        return res

    def traceback_l1(self, augmented_A, e, threshold=1e-6):
        m, n = augmented_A.shape
        e = e[0]
        n = n - 1

        model = Model()
        model.setParam('display/verblevel', 0)
        model.setParam("numerics/feastol", 1e-9)

        x_pos = {}
        x_neg = {}
        for i in range(m):
            x_pos[i] = model.addVar(lb=0.0, ub=1e4, vtype="C", name=f"x_pos_{i}")
            x_neg[i] = model.addVar(lb=0.0, ub=1e4, vtype="C", name=f"x_neg_{i}")

        model.setObjective(
            quicksum(x_pos[i] + x_neg[i] for i in range(m)),
            sense="minimize"
        )

        deltas = [x_pos[j] - x_neg[j] for j in range(m)]
        for i in range(n + 1):
            expr = []
            for j in range(m):
                coef = augmented_A[j, i]
                if coef != 0:
                    expr.append(coef * deltas[j])
            model.addCons(quicksum(expr) == e[i])
        
        model.optimize()

        if model.getStatus() == "optimal":
            x_values = [model.getVal(x_pos[i]) - model.getVal(x_neg[i]) for i in range(m)]
            indices = [i for i, val in enumerate(x_values) if abs(val) > threshold]
            return indices
        else:
            return None

    def traceback_l0(self, augmented_A, e) -> list[str]:
        m, n = augmented_A.shape
        e = e[0]
        n = n - 1

        model = Model()
        model.setParam('display/verblevel', 0)

        x = {}
        z = {}
        for i in range(m):
            x[i] = model.addVar(lb=-model.infinity(), ub=model.infinity(), vtype="C", name=f"x_{i}")
            z[i] = model.addVar(vtype="B", name=f"z_{i}")

        model.setObjective(quicksum(z[i] for i in range(m)), sense="minimize")

        for i in range(n + 1):
            expr = []
            for j in range(m):
                coef = augmented_A[j, i]
                if coef != 0:
                    expr.append(coef * x[j])
            model.addCons(quicksum(expr) == e[i])

        M = 10
        for i in range(m):
            model.addCons(x[i] <= M * z[i])
            model.addCons(x[i] >= -M * z[i])

        model.optimize()

        try:
            obj_val = model.getObjVal()
            indices = [i for i in range(m) if model.getVal(z[i]) > 1e-12]
            assert round(obj_val) == len(indices)
            return indices
        except:
            return None

    def vectorize(self, equations, variables, source):
        A = np.zeros((len(equations), len(variables)), dtype=np.float64)
        b = np.zeros((len(equations), 1), dtype=np.float64)

        if source in ("angle_linear", "length_linear"):
            for i, eqn in enumerate(equations):
                eqn = sympy.expand(eqn)
                terms = eqn.args if eqn.is_Add else (eqn,)
                for term in terms:
                    c, r = term.as_coeff_Mul()
                    syms = [f for f in sympy.Mul.make_args(r) if getattr(f, "is_Symbol", False) and f in variables]
                    if not syms:
                        b[i, 0] += float(c * r)
                    else:
                        if len(syms) != 1:
                            raise AssertionError(f"Nonlinear term: {term}")
                        var = syms[0]
                        others = [f for f in sympy.Mul.make_args(r) if f is not var]
                        coeff = float(c * (sympy.Mul(*others) if others else 1))
                        A[i, variables[var]] += coeff
        else:
            assert source == "length_ratio"
            for i, eqn in enumerate(equations):
                if isinstance(eqn, sympy.Mul):
                    div = 1
                    for arg in eqn.args:
                        if arg.is_number:
                            div *= arg
                    if div != 1:
                        eqn = eqn / div
                
                eqn = sympy.expand(eqn)

                probe = eqn.args if eqn.is_Add else (eqn,)
                const_sum0 = sum(float(t) for t in probe if not t.free_symbols)
                if const_sum0 > 0.0:
                    eqn = -eqn

                const_sum = 0.0
                terms = eqn.args if eqn.is_Add else (eqn,)

                for term in terms:
                    c, r = term.as_coeff_Mul()
                    sign = -1.0 if (c.is_number and c < 0) else 1.0
                    if sign < 0:
                        c = -c
                    mult = float(c)

                    exps = {}
                    for f in sympy.Mul.make_args(r):
                        if not f.free_symbols:
                            mult *= float(f)
                            continue
                        if isinstance(f, sympy.Pow):
                            base, exp = f.as_base_exp()
                            if base.is_Symbol and base in variables and exp.is_number:
                                e = float(exp)
                                exps[base] = exps.get(base, 0.0) + e
                                continue
                            if base.is_number and exp.is_number:
                                mult *= float(base) ** float(exp)
                                continue
                        if f.is_Symbol and f in variables:
                            exps[f] = exps.get(f, 0.0) + 1.0
                            continue
                        mult *= float(f)

                    if not exps:
                        const_sum += sign * mult
                        continue

                    for var, p in exps.items():
                        if p >= 0:
                            A[i, variables[var]] += sign * p
                        else:
                            A[i, variables[var]] -= sign * (-p)

                    if mult != 1.0:
                        if mult <= 0.0:
                            raise ValueError(f"Non-positive multiplier {mult} in term {term!r}")
                        b[i, 0] -= sign * math.log(mult)

                rhs = -const_sum
                if rhs > 0.0:
                    b[i, 0] += math.log(rhs)

        return np.concatenate([A, b], axis=1)

    def find_conditions(self, equations: list[Traced], conclusion, source):
        angle_linear, length_linear, length_ratio, others = classify_equations(equations, self.state.var_types)
        
        """Given sympified equations and conclusions, return a list of necessary conditions"""
        def try_find(equations, conclusion):
            variables = set()
            for eqn in equations:
                variables = variables.union(eqn.free_symbols)
            # Check if conclusion contains symbols not in equations
            conclusion_symbols = conclusion.free_symbols
            if not conclusion_symbols.issubset(variables):
                return None
            variables = {item: i for i, item in enumerate(list(variables))}
            mat = self.vectorize([item.expr for item in equations], variables, source)
            try:
                eq = self.vectorize([conclusion], variables, source)
            except:
                return None
            if self.norm == 1:
                deps = self.traceback_l1(mat, eq)
            else:
                assert self.norm == 0
                deps = self.traceback_l0(mat, eq)
            if deps:
                return [equations[i] for i in deps]
            else:
                return None
        
        if source == "angle_linear":
            equations = angle_linear
        elif source == "length_linear":
            equations = length_linear
        else:
            assert source == "length_ratio"
            equations = length_ratio
        return try_find(equations, conclusion)
