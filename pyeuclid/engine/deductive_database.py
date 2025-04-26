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
        self.name = id(self)
        self.inner_theorems = inner_theorems
        self.outer_theorems = outer_theorems
        self.closure = False
        self.sqliteConnection = sqlite3.connect(f"cache/{self.name}.db")
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
        self.visited = set()
        
    def __del__(self):
        self.sqliteConnection.close()
        os.remove(f"cache/{self.name}.db")

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

    def insert_points(self, *points):
        for point in points:
            query = f"INSERT OR IGNORE INTO points (name) VALUES ('{point}');"
            self.cursor.execute(query)
            
    def _sync(self):
        points = self.state.points
        relations = self.state.relations
        equivalence_classes = {"angle": self.state.angles.equivalence_classes().values(), "length": self.state.lengths.equivalence_classes().values(), "length_ratio": self.state.ratios.values(), "angle_sum": self.state.angle_sums.values()}
        self.insert_points(*list(points))
        for relation in relations:
            if type(relation) in [Equal]:
                continue
            self.insert_relation(relation)
        for table, components in equivalence_classes.items():
            self.update_equivalence_class(components, table)
        
    def insert_relation(self, relation: Relation):
        if relation.negated:
            return
        table = type(relation).__name__.lower()
        points = relation.get_points()
        cols = ",".join([f"p{i}" for i in range(len(points))])
        values = ",".join([f"'{item}'" for item in points])
        for point in points:
            query = f"INSERT OR IGNORE INTO points (name) VALUES ('{point}');"
            self.cursor.execute(query)
        query = f"""
        INSERT OR IGNORE INTO `{table}` ({cols})
        VALUES ({values});
        """
        self.cursor.execute(query)
        
    def update_equivalence_class(self, components, table):
        query = f"DELETE FROM {table}"
        if len(components) == 0:
            return
        self.cursor.execute(query)
        values = []
        for i, component in enumerate(components):
            for item in component:
                points = []
                symbols = str(item)
                if symbols.startswith("2*"):
                    symbols = f"{symbols[2:]}+{symbols[2:]}"
                symbols = symbols.replace("+", "/")
                symbols = symbols.split("/")
                for symbol in symbols:
                    points += symbol.split("_")[1:]
                tmp = [f"'{item}'" for item in points] + [str(i)]
                values.append(f"({','.join(tmp)})")
                cols = [f"p{i}" for i in range(len(points))]
        cols.append("component")
        cols = ", ".join(cols)
        values = ", ".join(values)
        query = f"INSERT OR IGNORE INTO {table} ({cols}) VALUES {values}"
        self.cursor.execute(query)
        
    def execute(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
            
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
            if isinstance(relation, Relation):
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
                points, _ = get_points_and_symbols(relation)
                
                def same_component(l, r, table):
                    query_diff = f" INNER JOIN {table} r{i}l INNER JOIN {table} r{i}r"
                    wheres_diff = []
                    perm1, perm2 = [], []
                    n_points = len(l) - 1
                    for j, item in enumerate(l):
                        perm1 += [f"r{i}l.p{j} = {item}.name"]
                        perm2 += [f"r{i}l.p{n_points-j} = {item}.name"]
                    perm1 = " AND ".join(perm1)
                    perm2 = " AND ".join(perm2)
                    wheres_diff += [f"({perm1} OR {perm2})"]
                    perm1, perm2 = [], []
                    for j, item in enumerate(r):
                        perm1 += [f"r{i}r.p{j} = {item}.name"]
                        perm2 += [f"r{i}r.p{n_points-j} = {item}.name"]
                    perm1 = " AND ".join(perm1)
                    perm2 = " AND ".join(perm2)
                    wheres_diff += [f"({perm1} OR {perm2})"]
                    wheres_diff += [f"r{i}l.component=r{i}r.component"]
                    return query_diff, wheres_diff
                
                def in_component(l: List[str], component_id, table):
                    query_diff = f" INNER JOIN {table} r{i} ON"
                    perm1, perm2 = [], []
                    n_points = len(l) - 1
                    for j, item in enumerate(l):
                        if not "." in str(item):
                            item = f"{item}.name"
                        perm1 += [f"r{i}.p{j} = {item}"]
                        perm2 += [f"r{i}.p{n_points-j} = {item}"]
                    perm1 = " AND ".join(perm1)
                    perm2 = " AND ".join(perm2)
                    query_diff += f"({perm1} OR {perm2}) AND r{i}.component={component_id}"
                    return query_diff
                
                def point_to_angle(formal_points):
                    query_diff = f" INNER JOIN angle angle{i} INNER JOIN angle angle_rep{i}"
                    wheres_diff = []
                    perm1 = [f"angle{i}.p0 = {formal_points[0]}.name", f"angle{i}.p1 = {formal_points[1]}.name", f"angle{i}.p2 = {formal_points[2]}.name"]
                    perm2 = [f"angle{i}.p2 = {formal_points[0]}.name", f"angle{i}.p1 = {formal_points[1]}.name", f"angle{i}.p0 = {formal_points[2]}.name"]
                    perm1, perm2 = " AND ".join(perm1), " AND ".join(perm2)
                    wheres_diff += [f"({perm1} OR {perm2})"]
                    wheres_diff += [f"angle{i}.component = angle_rep{i}.component"]
                    return query_diff, wheres_diff
                
                def point_to_ratio(formal_points):
                    query_diff = f" INNER JOIN length_ratio ratio{i} INNER JOIN length num{i} INNER JOIN length denom{i} INNER JOIN length num_rep{i} INNER JOIN length denom_rep{i}"
                    wheres_diff = []
                    perm1 = [f"num{i}.p0 = {formal_points[0]}.name", f"num{i}.p1 = {formal_points[1]}.name", f"denom{i}.p0 = {formal_points[2]}.name", f"denom{i}.p1 = {formal_points[3]}.name"]
                    perm2 =[f"num{i}.p0 = {formal_points[0]}.name", f"num{i}.p1 = {formal_points[1]}.name", f"denom{i}.p1 = {formal_points[2]}.name", f"denom{i}.p0 = {formal_points[3]}.name"]
                    perm3 =[f"num{i}.p1 = {formal_points[0]}.name", f"num{i}.p0 = {formal_points[1]}.name", f"denom{i}.p0 = {formal_points[2]}.name", f"denom{i}.p1 = {formal_points[3]}.name"]
                    perm4 = [f"num{i}.p1 = {formal_points[0]}.name", f"num{i}.p0 = {formal_points[1]}.name", f"denom{i}.p1 = {formal_points[2]}.name", f"denom{i}.p0 = {formal_points[3]}.name"]
                    perm1, perm2, perm3, perm4 = " AND ".join(perm1), " AND ".join(perm2), " AND ".join(perm3), " AND ".join(perm4)
                    wheres_diff += [f"({perm1} OR {perm2} OR {perm3} OR {perm4})"]
                    wheres_diff += [f"num{i}.component = num_rep{i}.component", f"denom{i}.component = denom_rep{i}.component"]
                    wheres_diff += [f"num_rep{i}.p0 = ratio{i}.p0", f"num_rep{i}.p1 = ratio{i}.p1", f"denom_rep{i}.p0 = ratio{i}.p2", f"denom_rep{i}.p1 = ratio{i}.p3"]
                    # no need for permutation, p0 always < p1
                    return query_diff, wheres_diff
                
                s = str(relation)
                if pattern_eqlength.match(s):
                    l, r = points[:2], points[2:]
                    query_diff, wheres_diff = same_component(l, r, "length")
                    query += query_diff
                    wheres += wheres_diff
                elif pattern_eqangle.match(s):
                    l, r = points[:3], points[3:]
                    query_diff, wheres_diff = same_component(l, r, "angle")
                    query += query_diff
                    wheres += wheres_diff
                elif pattern_eqratio.match(s): # join 2*(4point-2length-2length_rep-ratio)
                    l, r = points[:4], points[4:8]
                    i_bak = i
                    i = f"{i_bak}l"
                    query_diff, wheres_diff  = point_to_ratio(l)
                    query += query_diff
                    wheres += wheres_diff
                    i = f"{i_bak}r"
                    query_diff, wheres_diff  = point_to_ratio(r)
                    query += query_diff
                    wheres += wheres_diff
                    i = i_bak
                    wheres += [f"ratio{i}l.component=ratio{i}r.component"]
                elif pattern_angle_const.match(s):
                    left = points[:3]
                    cnst = [arg for arg in relation.args if len(arg.free_symbols)==0][0]
                    cnst = abs(cnst)
                    hit = False
                    for component_id, rep in enumerate(self.state.angles.equivalence_classes()):
                        if self.state.check_conditions(cnst - rep):
                            hit = True
                            break
                    if not hit:
                        return []
                    query += in_component(left, component_id, "angle")
                else: # join 2*(3point-angle-angle_rep)-angle_sum
                    assert pattern_angle_sum.match(s)
                    cnst = [arg for arg in relation.args if len(
                        arg.free_symbols) == 0][0]
                    cnst = abs(cnst)
                    hit = False
                    for component_id, rep in enumerate(self.state.angle_sums):
                        if self.state.check_conditions(cnst-rep):
                            hit = True
                            break
                    if not hit:
                        return []
                    l, r = points[:3], points[3:6]
                    i_bak = i
                    i = f"{i_bak}l"
                    query_diff, wheres_diff = point_to_angle(l)
                    query += query_diff
                    wheres += wheres_diff
                    i = f"{i_bak}r"
                    query_diff, wheres_diff = point_to_angle(r)
                    query += query_diff
                    wheres += wheres_diff
                    i = i_bak
                    query += in_component([f"angle_rep{i}l.p0", f"angle_rep{i}l.p1", f"angle_rep{i}l.p2", f"angle_rep{i}r.p0", f"angle_rep{i}r.p1", f"angle_rep{i}r.p2"], component_id, "angle_sum")
            else:
                if relation.negated:
                    continue # does not support negated condition
                table = type(relation).__name__.lower()
                assert table in relations
                query += f" INNER JOIN `{table}` r{i} ON "
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
                clause = f"({' OR '.join(permutation_clauses)})"
                query += clause
        if len(wheres) > 0:
            query += " WHERE " + " AND ".join(wheres)
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        results.sort()
        return results

    def get_applicable_theorems(self, theorems):
        self._sync()
        applicable_theorems = []
        pbar = tqdm(theorems, disable=self.state.silent)
        for theorem in pbar:
            pbar.set_description(
                f"{theorem.__name__} #rels {len(self.state.relations)} # eqns {len(self.state.equations)}")
            concrete_theorems = self.do_query(theorem)
            for i, points in enumerate(concrete_theorems):
                points = [Point(p) for p in points]
                concrete_theorems[i] = theorem(*points)
            applicable_theorems += concrete_theorems
        filtered = []
        for item in applicable_theorems:
            if not item in self.visited:
                self.visited.add(item)
                if self.state.check_conditions(item.condition()) and not item.degenerate():
                    filtered += [item]
        return filtered
    
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
