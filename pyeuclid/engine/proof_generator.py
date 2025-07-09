import math
import gurobipy as gp
import numpy as np
import sympy

from pyscipopt import Model, quicksum
from collections import defaultdict
from stopit import ThreadingTimeout as TT

from pyeuclid.formalization.relation import *
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.utils import *
from pyeuclid.engine.inference_rule import *


class ProofGenerator:
    def __init__(self, state, verbose=False):
        self.state = state
        self.visited = set()
        self.proof_dict = {}
        self.cache_conditions = {}
        self.cache_source = {}
        self.source_constructions = defaultdict(list)
        self.verbose = verbose
    
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
                expr_str_rep = str(sympy.simplify(node))
                for item in self.state.equations:
                    if item.depth < depth:
                        if expr_str_rep == item.str_rep or expr_str_rep == item.negated_str_rep:
                            node = item
                            break
            
            if isinstance(node, Traced):
                if node.str_rep in self.visited:
                    return self.source_constructions[node.str_rep]
                else:
                    self.visited.add(node.str_rep)
            else:
                if expr_str_rep in self.visited:
                    return self.source_constructions[expr_str_rep]
                else:
                    negated_expr_str_rep = str(sympy.simplify(-node))
                    self.visited.add(expr_str_rep)
                    self.visited.add(negated_expr_str_rep)
        
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
                if isinstance(sources[0], str):
                    # backtrace linear systems
                    equations = [item for item in self.state.equations if item.depth < node.depth]
                    if not node.symbol is None:
                        expr = node.symbol - node.expr
                    else:
                        expr = node.expr
                    
                    if node.str_rep in self.cache_conditions:
                        conditions = self.cache_conditions[node.str_rep]
                    elif node.negated_str_rep in self.cache_conditions:
                        conditions = self.cache_conditions[node.negated_str_rep]
                    else:
                        conditions = self.find_conditions(equations, expr, sources[0])
                    
                    discards = []
                    while len(conditions) > 6:
                        additional_equations = []
                        candidate_intermediate_conditions = [item for item in self.state.equations if item.depth == node.depth and item not in equations and item not in discards]

                        for intermediate_condition in candidate_intermediate_conditions:
                            if intermediate_condition.str_rep in self.cache_conditions:
                                if self.cache_source[intermediate_condition.str_rep] == sources[0]:
                                    cond = self.cache_conditions[intermediate_condition.str_rep]
                                else:
                                    cond = None
                            elif intermediate_condition.negated_str_rep in self.cache_conditions:
                                if self.cache_source[intermediate_condition.negated_str_rep] == sources[0]:
                                    cond = self.cache_conditions[intermediate_condition.negated_str_rep]
                                else:
                                    cond = None
                            else:
                                cond = self.find_conditions(equations, intermediate_condition.expr, sources[0])
                            
                            if cond:
                                if len(cond) <= 6:
                                    self.cache_conditions[intermediate_condition.str_rep] = cond
                                    self.cache_source[intermediate_condition.str_rep] = sources[0]
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
                    
                    self.cache_conditions[node.str_rep] = conditions
                    self.cache_source[node.str_rep] = sources[0]
                    sources = conditions
                else:
                    # inference rules derived traced
                    pass
                self.proof_dict[node.str_rep] = sources
                for item in sources:
                    cond_constructions = self.run(item, root=False)
                    constructions.update(cond_constructions)
                self.source_constructions[node] = sorted(constructions, key=lambda c: c.index)
                return self.source_constructions[node]
            else:
                assert isinstance(node, sympy.core.expr.Expr)
                source = None
                equations = [item for item in self.state.equations if item.depth < depth]

                str_rep = str(sympy.simplify(node))
                negated_str_rep = str(sympy.simplify(-node))

                if str_rep in self.cache_conditions:
                    conditions = self.cache_conditions[str_rep]
                    source = self.cache_source[str_rep]
                elif negated_str_rep in self.cache_conditions:
                    conditions = self.cache_conditions[negated_str_rep]
                    source = self.cache_source[negated_str_rep]
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
                while len(conditions) > 6:
                    additional_equations = []
                    candidate_intermediate_conditions = [item for item in self.state.equations if item.depth == depth and item not in equations and item not in discards]

                    for intermediate_condition in candidate_intermediate_conditions:
                        if intermediate_condition.str_rep in self.cache_conditions:
                            if self.cache_source[intermediate_condition.str_rep] == source:
                                cond = self.cache_conditions[intermediate_condition.str_rep]
                            else:
                                cond = None
                        elif intermediate_condition.negated_str_rep in self.cache_conditions:
                            if self.cache_source[intermediate_condition.negated_str_rep] == source:
                                cond = self.cache_conditions[intermediate_condition.negated_str_rep]
                            else:
                                cond = None
                        else:
                            cond = self.find_conditions(equations, intermediate_condition.expr, source)
                        
                        if cond:
                            if len(cond) <= 6:
                                self.cache_conditions[intermediate_condition.str_rep] = cond
                                self.cache_source[intermediate_condition.str_rep] = source
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

                self.cache_conditions[str_rep] = conditions
                self.cache_source[str_rep] = source
                sources = conditions
                self.proof_dict[str_rep] = sources
            
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
                if node.str_rep in visited:
                    return
                else:
                    visited.add(node.str_rep)
                    node = node.str_rep
            
            elif isinstance(node, sympy.core.expr.Expr):
                expr_str_rep = str(sympy.simplify(node))
                if expr_str_rep in self.proof_dict:
                    if expr_str_rep in visited:
                        return
                    else:
                        visited.add(expr_str_rep)
                        node = expr_str_rep
                else:
                    negated_expr_str_rep = str(sympy.simplify(-node))
                    assert negated_expr_str_rep in self.proof_dict
                    if negated_expr_str_rep in visited:
                        return
                    else:
                        visited.add(negated_expr_str_rep)
                        node = negated_expr_str_rep

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
            if type(theorem) in (DiagramAngle4a, DiagramAngle4b, DiagramAngle2, FlatAngle, FlatAngle2):
                return

            # Trace fundamental shape
            if len(conditions) == 1 and type(conditions[0]) in shape_dependency:
                condition, theorem = trace_fundamental_shape(conditions[0])
                conditions = [condition]
            
            for condition in conditions:
                format(condition)
            
            # Skip if all conditions are basic geometric relations
            if all([type(item) in (Collinear, Between, SameSide) for item in conditions]):
                return
            
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

    # TODO EQUATION STR
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
            res += f'{step+1}. ' + ' & '.join([str(item) for item in conditions]) + theorem_str + ' => ' + ' & '.join([str(item) for item in conclusions]) + '\n'
        return res
    
    def get_proof(self, node=None):
        res = []
        if not node and self.state.goal:
            node = self.state.goal
        
        proof_steps = self.format_proof(node)

        for proof_step in proof_steps:
            if not isinstance(proof_step['conditions'][0], ConstructionRule):
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
        # angle_linear = [eq for eq in equations if 'angle_linear' in eq.categories]
        # length_linear = [eq for eq in equations if 'length_linear' in eq.categories]
        # length_ratio = [eq for eq in equations if 'length_ratio' in eq.categories]
        # others = [eq for eq in equations if 'others' in eq.categories]
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
            deps = None
            # try:
            #     with TT(1):
            #         deps = self.traceback_l0(mat, eq)
            # except:
            #     pass
            
            # if not deps:
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
    
    def find_end_nodes(self):
        parent_nodes = set()
        for sources in self.proof_dict.values():
            if sources:
                parent_nodes.update(sources)

        all_nodes = set(self.proof_dict.keys())
        end_nodes = all_nodes - parent_nodes
        
        return list(end_nodes)