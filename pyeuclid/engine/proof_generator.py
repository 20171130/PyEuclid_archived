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
        
        if not node and self.state.goal:
            node = self.state.goal

        if root:
            depth = self.state.current_depth
        
        if depth is None:
            depth = node.depth
        
        if isinstance(node, (InferenceRule, Relation)):
            if node in self.visited:
                return self.source_constructions[node]
            else:
                self.visited.add(node)
        else:
            assert isinstance(node, (Traced, sympy.core.expr.Expr))
            if isinstance(node, sympy.core.expr.Expr):
                terms = node.as_ordered_terms()
                if isinstance(terms[0], sympy.core.mul.Mul) and terms[0].args[0].is_constant():
                    node = node/terms[0].args[0]
                
                for item in self.state.equations:
                    if item.depth < depth:
                        if item.expr == node:
                            node = item
                            break
            
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
                        cond_constructions = self.run(source, root=False)
                        constructions.update(cond_constructions)
                        self.source_constructions[node] = sorted(constructions, key=lambda c: c.index)
                        return self.source_constructions[node]
                    else:
                        return []
            else:
                assert False, f"{node} is not proved"
        else:
            if isinstance(node, Traced):
                # if not node.sources or type(node.sources[0]) in (DiagramAngle4a, DiagramAngle4b, DiagramAngle2, FlatAngle, FlatAngle2):
                #     sources = []
                # else:
                sources = node.sources
                expr = node.expr

                if isinstance(sources[0], str):
                    # backtrace linear systems
                    equations = [item for item in self.state.equations if item.depth < node.depth]
                    if expr in self.cache_conditions:
                        conditions = self.cache_conditions[expr]
                    else:
                        conditions = self.find_conditions(equations, expr, sources[0])
                    
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
                        
                    if not conditions:
                        breakpoint()
                        assert False
                    
                    self.cache_conditions[expr] = conditions
                    self.cache_source[expr] = sources[0]
                    sources = conditions
                else:
                    # inference rules derived traced
                    pass
                self.proof_dict[expr] = sources
                for item in sources:
                    cond_constructions = self.run(item, root=False)
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
                
                if not conditions:
                    breakpoint()
                    assert False

                self.cache_conditions[node] = conditions
                self.cache_source[node] = source
                sources = conditions
                self.proof_dict[node] = sources
            
                for item in sources:
                    cond_constructions = self.run(item, root=False)
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

    def track_constructions(self, condition=None):
        if not condition and self.state.goal:
            condition = self.state.goal
            
        def collect(node):
            if node in self.source_constructions:
                return self.source_constructions[node]

            if isinstance(node, ConstructionRule):
                return [node]

            constructions = set()

            if node in self.proof_dict:
                for parent in self.proof_dict[node]:
                    parent_constructions = collect(parent)
                    constructions.update(parent_constructions)
            
                self.source_constructions[node] = sorted(constructions, key=lambda c: c.index)
                return self.source_constructions[node]
            
            return []
        
        collect(condition)
    
    def show_proof(self, node=None):
        res = self.get_proof_str(node)
        print(res)

    def get_proof_str(self, node=None):
        res = "Solution:\n"
        proof = self.get_proof(node)
        for step, (conditions, theorem, conclusions) in enumerate(proof):
            theorem_str = ' [' + str(theorem) + ']' if theorem else ''
            # theorem_str = ''
            res += f'{step+1}. ' + ' & '.join([str(item) for item in conditions]) + theorem_str + ' => ' + ' & '.join([str(item) for item in conclusions]) + '\n'
        return res
    
    def get_proof(self, node=None):
        res = []
        if not node and self.state.goal:
            node = self.state.goal
        
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
        
        try:
            x_values = [model.getVal(x_pos[i]) - model.getVal(x_neg[i]) for i in range(m)]
            indices = [i for i, val in enumerate(x_values) if abs(val) > threshold]
            return indices
        except:
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
                assert isinstance(eqn, sympy.core.add.Add) or isinstance(eqn, sympy.core.symbol.Symbol)

                for add_arg in eqn.args:
                    if len(add_arg.args) == 0:
                        mul_args = [add_arg]
                    else:
                        assert isinstance(add_arg, sympy.core.mul.Mul)
                        mul_args = add_arg.args
                    factors = [item for item in mul_args if len(
                        item.free_symbols) == 0]
                    factor = sympy.core.mul.Mul(*factors)
                    symbols = [item for item in mul_args if len(
                        item.free_symbols) > 0]
                    if len(symbols) == 0:
                        b[i, 0] = factor.evalf()
                    else:
                        A[i, variables[symbols[0]]] = factor.evalf()
        else:
            assert source == "length_ratio"  # length=const or eqlength or eqlength ratio or lengthratio=const
            for i, eqn in enumerate(equations):
                if isinstance(eqn, sympy.core.add.Add):
                    if len(eqn.args) > 2:
                        breakpoint()
                        assert False
                    add_args = eqn.args
                else:
                    add_args = [eqn]
                for j, add_arg in enumerate(add_args):
                    if len(add_arg.args) > 0:
                        mul_args = add_arg.args
                    else:
                        mul_args = [add_arg]
                    for mul_arg in mul_args:
                        factor = (-1)**(j)
                        if isinstance(mul_arg, sympy.core.power.Pow):
                            factor *= mul_arg.args[1]
                            mul_arg = mul_arg.args[0]
                        if len(mul_arg.free_symbols) == 0:
                            b[i, 0] += factor * math.log(abs(mul_arg))
                        else:
                            symbol = list(mul_arg.free_symbols)[0]
                            A[i, variables[symbol]] += factor
        return np.concat([A, b], axis=1)

    def find_conditions(self, equations: list[Traced], conclusion, source):
        angle_linear, length_linear, length_ratio, others = classify_equations(equations, self.state.var_types)
        """Given sympified equations and conclusions, return a list of necessary conditions"""
        def try_find(equations, conclusion):
            variables = set()
            for eqn in equations:
                variables = variables.union(eqn.free_symbols)
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
