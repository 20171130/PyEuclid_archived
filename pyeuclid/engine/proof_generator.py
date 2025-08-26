import math
import numpy as np
import sympy

from pyscipopt import Model, quicksum
from collections import defaultdict

from pyeuclid.formalization.relation import *
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.utils import *
from pyeuclid.engine.inference_rule import *


class ProofGenerator:
    def __init__(self, state):
        self.state = state
        self.visited = set()
        self.proof_dict = {}
        self.cache_conditions = {}
        self.cache_source = {}
        self.source_constructions = defaultdict(list)
        self.max_equation_length_perstep = 6
    
    def run(self, node=None, depth=None, root=True):
        if isinstance(node, ConstructionRule):
            return [node]
        
        if root or depth is None:
            depth = self.state.current_depth
        
        depth = min(getattr(node, "depth", self.state.current_depth), depth)
            
        if not node and self.state.goal:
            node = self.state.goal
            if not (self.state.complete() == 0 or self.state.complete() is True):
                if "angle" in str(node).lower() or self.state.var_types.get(node, None) =="Angle":
                    source = "angle_linear"
                else: # including Area
                    source = "length_ratio"
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
            self.source_constructions[node] = sorted(constructions, key=lambda c: c.index)
            return self.source_constructions[node]

        elif isinstance(node, Relation):
            for tmp in self.state.relations:
                if tmp == node:
                    if hasattr(tmp, "source"):
                        source = tmp.source
                        self.proof_dict[node] = [source]
                        cond_constructions = self.run(source, depth=depth, root=False)
                        constructions.update(cond_constructions)
                        self.source_constructions[node] = sorted(constructions, key=lambda c: c.index)
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
                    self.proof_dict[node] = []
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
                for item in sources:
                    cond_constructions = self.run(item, depth=depth, root=False)
                    constructions.update(cond_constructions)
                self.source_constructions[expr] = sorted(constructions, key=lambda c: c.index)
                return self.source_constructions[expr]
            else:
                assert isinstance(node, sympy.core.expr.Expr)
                source = None
                equations = [item for item in self.state.equations if item.depth < depth]
                if node in self.cache_conditions:
                    conditions = self.cache_conditions[node]
                    source = self.cache_source[node]
                else:
                    if "Angle" in str(node):
                        source = "angle_linear"
                        conditions = self.find_conditions(equations, node, source)
                    else:
                        for tmp in ("length_ratio", "length_linear"):
                            conditions = self.find_conditions(equations, node, tmp)
                            if conditions:
                                source = tmp
                                break
                if conditions is None:
                    conditions = []
                    expr = node
                    symbols = [symbol for symbol in node.free_symbols if symbol in self.state.solutions]
                    for symbol in symbols:
                        expr = expr.subs(symbol, self.state.solutions[symbol])
                        conditions.append(symbol - self.state.solutions[symbol])
                        if expr == 0:
                            break
                    else:
                        breakpoint()
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
            
                for item in sources:
                    cond_constructions = self.run(item, root=False, depth=depth)
                    constructions.update(cond_constructions)
                
                self.source_constructions[node] = sorted(constructions, key=lambda c: c.index)
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
            
            # print('node', node, 'step_counter', step_counter, 'conditions', conditions)
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
    
    def show_proof(self, node=None, verbose=False):
        res = self.get_proof_str(node, verbose)
        print(res)

    def get_proof_str(self, node=None, verbose=False):
        res = "Solution:\n"
        proof = self.get_proof(node)
        def _format(items):
            if verbose:
                return ' & '.join([str(item)+ (f"@{item.depth}" if hasattr(item, 'depth') else "") for item in items])
            return ' & '.join([str(item) for item in items])
        for step, (conditions, theorem, conclusions) in enumerate(proof):
            if verbose:
                theorem_str = ' [' + str(theorem) + ']' if theorem else ''
            else:
                theorem_str = ''
            res += f'{step+1}. ' + _format(conditions) + theorem_str + ' => ' + _format(conclusions) + '\n'
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

        x_pos = {}
        x_neg = {}
        for i in range(m):
            x_pos[i] = model.addVar(lb=0.0, vtype="C", name=f"x_pos_{i}")
            x_neg[i] = model.addVar(lb=0.0, vtype="C", name=f"x_neg_{i}")

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
        A = np.zeros(shape=(len(equations), len(variables)), dtype=np.float64)
        b = np.zeros(shape=(len(equations), 1), dtype=np.float64)
        if source in ("angle_linear", "length_linear"):
            for i, eqn in enumerate(equations):
                eqn = sympy.expand(eqn)
                if isinstance(eqn, sympy.Add):
                    terms = eqn.args
                else:
                    terms = [eqn]

                for term in terms:
                    mul_args = sympy.Mul.make_args(term)
                    constants = [f for f in mul_args if not f.free_symbols]
                    symbols = [f for f in mul_args if f.free_symbols]

                    coeff = sympy.Mul(*constants)

                    if len(symbols) == 0:
                        b[i, 0] += coeff
                    else:
                        assert len(symbols) == 1, f"Nonlinear term: {term}"
                        var = symbols[0]
                        assert var in variables
                        A[i, variables[var]] += coeff
        else:
            assert source == "length_ratio"  # length=const or eqlength or eqlength ratio or lengthratio=const      
            for i, eqn in enumerate(equations):
                if isinstance(eqn, sympy.Add):
                    terms = eqn.args
                else:
                    terms = [eqn]
                
                for term in terms:
                    # Extract sign from the term
                    if isinstance(term, sympy.Mul) and len(term.args) > 0 and term.args[0].is_number and term.args[0] < 0:
                        sign = -1
                        # Remove the negative sign for processing
                        if len(term.args) == 1:
                            term = -term.args[0]  # Just a negative number
                        else:
                            # Multiply by -1 to make positive, then we'll apply sign later
                            term = sympy.Mul(*[-term.args[0]] + list(term.args[1:]))
                    elif term.is_number and term < 0:
                        sign = -1
                        term = -term
                    else:
                        sign = 1
                    
                    # Now process the positive term and apply sign at the end
                    numerator_vars = {}
                    denominator_vars = {}
                    constant_num = 1
                    constant_den = 1
                    
                    if isinstance(term, sympy.Mul):
                        for factor in term.args:
                            if factor.is_number:
                                constant_num *= float(factor)
                            elif factor.is_symbol and factor in variables:
                                numerator_vars[factor] = numerator_vars.get(factor, 0) + 1
                            elif isinstance(factor, sympy.Pow):
                                base, exp = factor.args
                                exp_val = float(exp)
                                if base.is_symbol and base in variables:
                                    if exp_val > 0:
                                        numerator_vars[base] = numerator_vars.get(base, 0) + exp_val
                                    else:
                                        denominator_vars[base] = denominator_vars.get(base, 0) + abs(exp_val)
                                elif base.is_number:
                                    if exp_val > 0:
                                        constant_num *= float(base) ** exp_val
                                    else:
                                        constant_den *= float(base) ** abs(exp_val)
                            elif isinstance(factor, (sympy.core.numbers.Rational, sympy.core.numbers.Float)):
                                constant_num *= float(factor)
                            else:
                                try:
                                    val = float(factor)
                                    constant_num *= val
                                except:
                                    pass
                                    
                    elif isinstance(term, sympy.Pow):
                        base, exp = term.args
                        exp_val = float(exp)
                        if base.is_symbol and base in variables:
                            if exp_val > 0:
                                numerator_vars[base] = exp_val
                            else:
                                denominator_vars[base] = abs(exp_val)
                        elif base.is_number:
                            if exp_val > 0:
                                constant_num = float(base) ** exp_val
                            else:
                                constant_den = float(base) ** abs(exp_val)
                                
                    elif term.is_symbol and term in variables:
                        numerator_vars[term] = 1
                        
                    elif term.is_number or isinstance(term, (sympy.core.numbers.Rational, sympy.core.numbers.Float)):
                        constant_num = float(term)
                        
                    else:
                        try:
                            constant_num = float(term)
                        except:
                            assert False
                    
                    # Apply to matrix with correct sign
                    # Numerator variables contribute positively
                    for var, power in numerator_vars.items():
                        A[i, variables[var]] += sign * power
                    
                    # Denominator variables contribute negatively  
                    for var, power in denominator_vars.items():
                        A[i, variables[var]] -= sign * power
                    
                    # Handle constants
                    if constant_num != 1 or constant_den != 1:
                        const_contribution = constant_num / constant_den
                        if const_contribution > 0:
                            b[i, 0] += sign * math.log(const_contribution)
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
            deps = self.traceback_l1(mat, eq)
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
