from tqdm import tqdm
import inspect
import sqlite3
import os
import re
import sympy
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.state import *
from pyeuclid.engine.inference_rule import *

class DeductiveDatabase():
    def __init__(self, state, inner_theorems=inference_rule_sets["ex"], outer_theorems=inference_rule_sets["basic"]):
        self.state = state
        self.inner_theorems = inner_theorems
        self.outer_theorems = outer_theorems
        self.closure = False
        self.sqliteConnection = sqlite3.connect("sql.db")
        self.cursor = self.sqliteConnection.cursor()
        points = """ CREATE TABLE points (
                    name CHAR(10) PRIMARY KEY NOT NULL
                ); """
        self.cursor.execute(points)
        for name, rel in relations.items():
            args = inspect.getfullargspec(rel)
            npoints = len(args[0]) - 1
            self._create_table(f"`{name}`", npoints)
        self._create_table("angle", 3, True)
        self._create_table("angle_sum", 6, True)
        self._create_table("length", 2, True)
        self._create_table("length_ratio", 4, True)
        
    def __del__(self):
        self.sqliteConnection.close()
        os.remove("sql.db")

    def _create_table(self, name, n_points, equivalence=False):
        query = ", ".join([f"p{i} CHAR(10) NOT NULL" for i in range(n_points)])
        if equivalence:
            query += f", component INT"
        query += ", "
        query += ", ".join([f"FOREIGN KEY(p{i}) REFERENCES points(name)" for i in range(n_points)])
        primary = ", ".join([f"p{i}" for i in range(n_points)])
        query += f" PRIMARY KEY ({primary})"
        query = f"CREATE TABLE {name} ({query});"
        self.cursor.execute(query)
        return query

    def insert_relation(self, relation: Relation):
        table = type(relation).__name__.lower()
        points = relation.get_points()
        cols = ",".join([f"p{i}" for i in range(len(points))])
        values = ",".join([f"'{item}'" for item in points])
        for point in points:
            query = f"INSERT OR IGNORE INTO points (name) VALUES ('{point}');"
            self.cursor.execute(query)
        query = f"""
        INSERT OR IGNORE INTO {table} ({cols})
        VALUES ({values});
        """
        self.cursor.execute(query)
        
    def update_equivalence_class(self, components, table):
        query = f"DELETE FROM {table}"
        self.cursor.execute(query)
        values = []
        for i, component in enumerate(components):
            for item in component:
                points = str(item).split("_")[1:]
                tmp = [f"'{item}'" for item in points] + [str(i)]
                values.append(f"({','.join(tmp)})")
                cols = [f"p{i}" for i in range(len(points))]
        cols.append("component")
        cols = ", ".join(cols)
        values = ", ".join(values)
        query = f"INSERT INTO {table} ({cols}) VALUES {values}"
        self.cursor.execute(query)
            
    def do_query(self, inference: InferenceRule):
        query = "SELECT "
        formal_points = inspect.getfullargspec(inference)[0][1:]
        formal_points = [Point(item) for item in formal_points]
        condition = inference(*formal_points).condition()
        for point in formal_points:
            query += f"{point}.name, "
        query = query[:-2] + " "
        query += "FROM "
        for point in formal_points:
            query += f"points {point}, "
        query = query[:-2]
        wheres = []
        for i, relation in enumerate(condition):
            points = relation.get_points()
            if isinstance(relation, Lt):
                assert not relation.negated
                wheres += [f"{points[0]}.name < {points[1]}.name"]
            elif isinstance(relation, Equal):
                assert relation.negated
                wheres += [f"{points[0]}.name != {points[1]}.name"]
            elif isinstance(relation, sympy.core.expr.Expr):
                pattern_eqlength = re.compile(r"^-?Length\w+ [-\+] Length\w+$")
                pattern_eqangle = re.compile(r"^-?Angle\w+ [-\+] Angle\w+$")
                pattern_eqratio = re.compile(
                    r"^-?Length\w+/Length\w+ [\+-] Length\w+/Length\w+$")
                pattern_angle_const = re.compile(
                    r"^-?Angle\w+ [-\+] [\w/\d]+$")
                pattern_angle_sum = re.compile(
                    r"^-?Angle\w+ [-\+] Angle\w+ [-\+] [\w/\d]+$")
                points, _ = get_points_and_symbols(cond)
                def same_component(l, r, table):
                    query = f"INNER JOIN {table} r{i}l, INNER JOIN {table} r{i}r"
                    for j, item in enumerate(l):
                        wheres += [f"r{i}l.p{j} = {item}.name"]
                    for j, item in enumerate(r):
                        wheres += [f"r{i}r.p{j} = {item}.name"]
                    wheres += [f"r{i}l.component=r{i}r.component"]
                    return query
                def in_component(l, component_id, table):
                    query = f"INNER JOIN {table} r{i} ON"
                    for j, item in enumerate(l):
                        query += f"r{i}.p{j} = {item} AND"
                    query += f"r{i}l.component={component_id}"
                    return query
                def point_to_ratio(formal_points):
                    query = f"INNER JOIN length_ratio r{i}, INNER JOIN length r{i}0, INNER JOIN length r{i}1, INNER JOIN length r{i}2, INNER JOIN length r{i}3"
                    wheres += [f"r{i}0.p0 = {formal_points[0]}.name", f"r{i}0.p1 = {formal_points[1]}.name", f"r{i}1.p0 = {formal_points[2]}.name", f"r{i}1.p1 = {formal_points[3]}.name"]
                    wheres += [f"r{i}0.component = r{i}2.component", f"r{i}1.component = r{i}3.component"]
                    wheres += [f"r{i}2.p0 = r{i}.p0", f"r{i}2.p1 = r{i}.p1", f"r{i}3.p0 = r{i}.p2", f"r{i}3.p1 = r{i}.p3"]
                    return query
                if pattern_eqlength.match(relation):
                    l, r = points[:2], points[2:]
                    query += same_component(l, r)
                elif pattern_eqangle.match(relation):
                    l, r = points[:3], points[3:]
                    query += same_component(l, r)
                elif pattern_eqratio.match(relation): # join 2*(point-length-length-ratio)
                    l, r = points[:4], points[4:8]
                    i_bak = i
                    i = f"{i_bak}l"
                    l = point_to_ratio(l)
                    i = f"{i_bak}r"
                    r = point_to_ratio(r)
                    i = i_bak
                    wheres += [f"r{i}l.component=r{i}r.component"]
                    query += l + r
                elif pattern_angle_const.match(relation):
                    left = points[:3]
                    cnst = [arg for arg in relation.args if len(arg.free_symbols)==0][0]
                    cnst = abs(cnst)
                    for rep, component in self.state.angles.equivalence_classes().items():
                        if self.state.check_conditions(cnst - rep):
                            query += in_component(left, component)
                            break
                else:
                    assert pattern_angle_sum.match(relation)
                    cnst = [arg for arg in relation.args if len(
                        arg.free_symbols) == 0][0]
                    cnst = abs(cnst)
                    left, right = points[:3], points[3:]
                    for rep, angle_sums in self.state.angle_sums.items():
                        if self.state.check_conditions(cnst-rep):
                            for angle_sum in angle_sums:
                                if isinstance(angle_sum, sympy.core.add.Add):
                                    angle1, angle2 = angle_sum.args
                                    # angle1 + angle2
                                else:
                                    angle1 = list(angle_sum.free_symbols)[0]
                                    angle2 = angle1
                                    # 2 * angle_1
                                angle1, angle2 = self.state.angles.find(angle1), self.state.angles.find(angle2)
                                component1, component2 = self.state.angles.equivalence_classes(
                                )[angle1], self.state.angles.equivalence_classes()[angle2]
                                wheres += in_component(angle1, component1)
                                wheres += in_component(angle2, component2)
                            break
            else:
                table = type(relation).__name__.lower()
                assert table in relations
                query += f" INNER JOIN {table} r{i} ON "
                if hasattr(relation, "permutations"):
                    permutations = relation.permutations()
                else:
                    permutations = [points]
                permutation_clauses = []
                for permutation in permutations:
                    point_atoms = []
                    for j, point in enumerate(permutation):
                        point_atoms.append(f"{point}.name = r{i}.p{j}")
                    permutation_clauses.append(f"({" AND ".join(point_atoms)})")
                query += " OR ".join(permutation_clauses)
        query += " WHERE " + " AND ".join(wheres)
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results

        
    def get_applicable_theorems(self, theorems):
        applicable_theorems = []
        pbar = tqdm(theorems, disable=self.state.silent)
        for theorem in pbar:
            pbar.set_description(
                f"{theorem.__name__} #rels {len(self.state.relations)} # eqns {len(self.state.equations)}")
            concrete_theorems = self.do_query(theorem)
            applicable_theorems += concrete_theorems
        return applicable_theorems
    
    def apply(self, inferences):
        last = None
        cnt = 0
        for item in inferences:
            tmp = type(item)
            if not tmp == last:
                if cnt > 3:
                    if not self.state.silent:
                        self.state.logger.info(f"...and {cnt-3} more.")
                cnt = 0
                last = tmp
            if cnt < 3:
                if not self.state.silent:
                    self.state.logger.info(str(item))
            cnt += 1
            conclusions = item.conclusion()
            for i, conclusion in enumerate(conclusions):
                if isinstance(conclusion, sympy.core.expr.Expr):
                    conclusion = Traced(conclusion)
                    conclusion.sources = [item]
                else:
                    conclusion.source = item
                conclusion.depth = self.state.current_depth
                item.depth = self.state.current_depth
                conclusions[i] = conclusion
            self.state.add_relations(conclusions)
        if cnt > 3:
            if not self.state.silent:
                self.state.logger.info(f"...and {cnt - 3} more.")
    
    def run(self):
        inner_closure = True
        while True:
            if self.state.complete() is not None:
                return
            inner_applicable = self.get_applicable_theorems(self.inner_theorems)
            self.apply(inner_applicable)
            if len(inner_applicable) == 0:
                break
            inner_closure = False
            
        if self.state.complete() is not None:
            return
        
        applicable_theorems = self.get_applicable_theorems(self.outer_theorems)
        self.apply(applicable_theorems)
        
        if len(applicable_theorems) == 0 and inner_closure:
            self.closure = True
            if not self.state.silent:
                self.state.logger.debug("Found Closure")
            return