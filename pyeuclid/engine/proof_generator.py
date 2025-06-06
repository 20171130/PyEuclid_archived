import math
import gurobipy as gp
import numpy as np
import sympy

from pyscipopt import Model, quicksum
from collections import defaultdict

from pyeuclid.formalization.relation import *
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.utils import *
from pyeuclid.engine.inference_rule import *


class ProofGenerator:
    def __init__(self, state, verbose=False):
        self.state = state
        self.visited = set()
        self.proof_dict = {}
        self.source_constructions = defaultdict(set)
        self.verbose = verbose
    
    def run(self, node=None, depth=None, root=True):
        if not node and self.state.goal:
            node = self.state.goal
        
        if root:
            depth = self.state.current_depth

        if isinstance(node, ConstructionRule):
            self.visited.add(node)
            return
        
        if node in self.visited:
            return
        
        if depth is None:
            depth = node.depth
        
        if isinstance(node, InferenceRule):
            self.visited.add(node)
            conds = [item for item in node.condition() if type(item)
                     not in (Different2, Lt) and not item == 0]
            self.proof_dict[node] = conds
            for cond in conds:
                self.run(cond, depth=depth-1, root=False)
        
        elif isinstance(node, Relation):
            self.visited.add(node)
            if trivial_condition(node):
                return
            for tmp in self.state.relations:
                if tmp == node:
                    if hasattr(tmp, "source"):
                        source = tmp.source
                        self.proof_dict[node] = [source]
                        self.run(source, root=False)
                    break
            else:
                assert False, f"{node} is not proved"
        else:
            if isinstance(node, Traced):
                sources = node.sources
                if isinstance(sources[0], str):
                    # backtrace linear systems
                    equations = [item for item in self.state.equations if item.depth <= node.depth]
                    if not node.symbol is None:
                        expr = node.symbol - node.expr
                    else:
                        expr = node.expr
                    conditions = self.find_conditions(equations, expr, sources[0])
                    if not conditions:
                        breakpoint()
                        assert False
                    sources = conditions
                else:
                    self.visited.add(node)
            else:
                assert isinstance(node, sympy.core.expr.Expr)
                sources = []
                depth = min(int(depth), len(self.state.solutions)-1)
                equations = [item for item in self.state.equations if item.depth <= depth]
                if "Angle" in str(node):
                    conditions = self.find_conditions(equations, node, "angle_linear")
                else:
                    for tmp in ("length_ratio", "length_linear"):
                        conditions = self.find_conditions(equations, node, tmp)
                        if conditions:
                            break
                if not conditions:
                    breakpoint()
                    assert False
                sources = conditions
            self.proof_dict[node] = sources
            for item in sources:
                self.run(item, root=False)
        
        if root and self.verbose:
            self.show_proof()

    def track_constructions(self, condition=None):
        if not condition and self.state.goal:
            condition = self.state.goal
        
        def refine_constructions(constructions):
            require_points = {p for construction in constructions for p in construction.inputs}
            produced_points = {p for construction in constructions for p in construction.outputs}
            
            missing_points = require_points - produced_points
            return constructions.union({self.state.point2construction[p] for p in missing_points})
            
        def collect(node):
            if node in self.source_constructions:
                return self.source_constructions[node]

            if isinstance(node, ConstructionRule):
                return [node]

            constructions = set()

            if node in self.proof_dict:
                for child in self.proof_dict[node]:
                    child_constructions = collect(child)
                    constructions.update(child_constructions)
                
                constructions = refine_constructions(constructions)
                self.source_constructions[node] = constructions
            
            return constructions
        
        collect(condition)
    
    def format_proof(self, conclusion=None):
        proof = []
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
            if node in visited or node not in self.proof_dict or self.proof_dict[node] is None:
                return
            visited.add(node)
            conditions = self.proof_dict[node]
            theorem = None
            while len(conditions) == 1 and conditions[0] in self.proof_dict: # collapse single-condition inferences
                if isinstance(conditions[0], InferenceRule) and not type(conditions[0]) in inference_rule_sets["ex"]:
                    theorem = conditions[0]
                conditions = self.proof_dict[conditions[0]]
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

        if not conclusion and self.state.goal:
            conclusion = self.state.goal

        search(conclusion)
        lst = [(key, value) for key, value in proof_steps.items()]
        lst.sort(key=lambda x: x[1][0])
        last = -1
        for node, (step_number, conditions, theorem) in lst:
            if step_number == last:
                continue
            last = step_number
            dic = {"condition": conditions, "step": step_number, "theorem": theorem, "conclusion": node}
            proof.append(dic)
        
        return proof
        
    def show_proof(self, node=None):
        if not node and self.state.goal:
            node = self.state.goal
        
        proof = self.format_proof(node)

        step = 1
        for proof_step in proof:
            if not isinstance(proof_step['condition'][0], ConstructionRule):
                print(f'{step}. ' + ' & '.join(str(item) for item in proof_step['condition'] if not trivial_condition(item)) + ' => ' + str(proof_step['conclusion']))
                step += 1

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

        for i in range(n + 1):
            model.addCons(
                quicksum(augmented_A[j, i] * (x_pos[j] - x_neg[j]) for j in range(m)) == e[i]
            )

        model.optimize()
        x_values = [model.getVal(x_pos[i]) - model.getVal(x_neg[i]) for i in range(m)]
        indices = [i for i, val in enumerate(x_values) if abs(val) > threshold]

        return indices


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
            model.addCons(quicksum(augmented_A[j, i] * x[j] for j in range(m)) == e[i])

        M = 10
        for i in range(m):
            model.addCons(x[i] <= M * z[i])
            model.addCons(x[i] >= -M * z[i])

        model.optimize()

        obj_val = model.getObjVal()

        indices = [i for i in range(m) if model.getVal(z[i]) > 0.5]

        assert round(obj_val) == len(indices)
        
        return indices

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
            eq = self.vectorize([conclusion], variables, source)
            try:
                with Timeout(60):
                    deps = self.traceback_l0(mat, eq)
            except:
                deps = self.traceback_l1(mat, eq)

            return [equations[i] for i in deps]
        
        if source == "angle_linear":
            equations = angle_linear
        elif source == "length_linear":
            equations = length_linear
        else:
            assert source == "length_ratio"
            equations = length_ratio
        return try_find(equations, conclusion)
    
    