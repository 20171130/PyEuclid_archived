from collections import Counter

from pyeuclid.formalization.relation import *
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.utils import is_float


def get_constructions_list_from_text(text):
    parts = text.split(' ? ')
    constructions_text_list = parts[0].split('; ')
    constructions_list = []
    
    for constructions_text in constructions_text_list:
        outputs_text, constructions_text = constructions_text.split(' = ')
        construction_text_list = constructions_text.split(', ')
        output_names = [name.replace('_', '') for name in outputs_text.split(' ')]
        outputs = [Point(name) for name in output_names]
        constructions = []
        for construction_text in construction_text_list:
            construction_text = construction_text.split(' ')
            rule_name = construction_text[0]
            arg_names = [name.replace('_', '') for name in construction_text[1:]]
            rule = globals()['construct_'+rule_name]
            all_args = [float(arg_name) if is_float(arg_name) else Point(arg_name) for arg_name in arg_names]
            if len(all_args) != rule.num_inputs + rule.num_outputs:
                all_args = outputs + all_args
            assert len(all_args) == rule.num_inputs + rule.num_outputs
            
            if rule_name == 'parallelogram' or rule_name == 'square':
                inputs, outputs = all_args[:rule.num_inputs], all_args[rule.num_inputs:]
            elif rule_name == 's_angle':
                inputs, outputs = all_args[:2] + [all_args[3]], [all_args[2]]
            else:
                outputs, inputs = all_args[:rule.num_outputs], all_args[rule.num_outputs:]
            
            construction = rule(*inputs)
            construction.construct(*outputs)
            constructions.append(construction)
        constructions_list.append(constructions)
    
    return constructions_list

def get_constructions_from_goal(goal):
    if isinstance(goal, Relation):
        if isinstance(goal, Concyclic):
            a, b, c, d = goal.get_points()
            return [construct_connect(a, b), construct_connect(b, c), construct_connect(c, d), construct_connect(d, a)]
        elif isinstance(goal, Collinear):
            a, b, c = goal.get_points()
            return [construct_connect(a, b), construct_connect(b, c), construct_connect(c, a)]
        elif isinstance(goal, Perpendicular):
            a, b, c, d = goal.get_points()
            return [construct_connect(a, b), construct_connect(c, d)]
        elif isinstance(goal, Parallel):
            a, b, c, d = goal.get_points()
            return [construct_connect(a, b), construct_connect(c, d)]
        elif isinstance(goal, Midpoint):
            a, b, c = goal.get_points()
            return [construct_connect(a, b), construct_connect(b, c), construct_connect(c, a)]
        elif isinstance(goal, Similar3):
            a, b, c, d, e, f = goal.get_points()
            return [construct_connect(a, b), construct_connect(b, c), construct_connect(c, a), construct_connect(d, e), construct_connect(e, f), construct_connect(f, d)]
        elif isinstance(goal, Congruent3):
            a, b, c, d, e, f = goal.get_points()
            return [construct_connect(a, b), construct_connect(b, c), construct_connect(c, a), construct_connect(d, e), construct_connect(e, f), construct_connect(f, d)]
        else:
            return []
    else:

        # classify angles - angles, angles + angles - const, angles - const, angles / angles - const,
        # lengths - lenghs, lengths + lengths - const, lengths - const, lengths / lengths - const, length/length - length/length 
        res = []
        points_list, symbols = get_points_and_symbols(goal)
        for points, symbol in zip(points_list, symbols):
            if 'Length' in str(symbol):
                assert len(points) == 2
                res.append(construct_connect(points[0], points[1]))
            elif 'Angle' in str(symbol):
                assert len(points) == 3
                res.append(construct_connect(points[0], points[1]), construct_connect(points[1], points[2]))
            else:
                l = len(points)
                for i in range(l-1):
                    res.append(construct_connect(points[i], points[i+1]))
                res.append(construct_connect(points[l-1], points[0]))
        return res


def get_goal_from_text(text):
    parts = text.split(' ? ')
    goal_text = parts[1] if len(parts) > 1 else None
    goal = None
    if goal_text:
        goal_text = goal_text.split(' ')
        goal_name = goal_text[0]
        arg_names = [name.replace('_', '') for name in goal_text[1:]]
        args = [Point(arg_name) for arg_name in arg_names]
        if goal_name == 'cong':
            goal = Length(*args[:2]) - Length(*args[2:])
        elif goal_name == 'cyclic':
            goal = Concyclic(*args)
        elif goal_name == 'coll':
            goal = Collinear(*args)
        elif goal_name == 'perp':
            goal = Perpendicular(*args)
        elif goal_name == 'para':
            goal = Parallel(*args)
        elif goal_name == 'eqratio':
            goal = Length(*args[:2])/Length(*args[2:4]) - Length(*args[4:6])/Length(*args[6:8])
        elif goal_name == 'eqangle':
            def extract_angle(points):
                count = Counter(points)
                repeating = next(p for p, c in count.items() if c == 2)
                singles = [p for p, c in count.items() if c == 1]
                return singles[0], repeating, singles[1]
            angle1 = Angle(*extract_angle(args[:4]))
            angle2 = Angle(*extract_angle(args[4:]))
            # The goal may involve either equal angles or supplementary angles
            goal = (angle1 - angle2, angle1 + angle2 - pi)
        elif goal_name == 'midp':
            goal = Midpoint(*args)
        elif goal_name == 'simtri':
            goal = Similar(*args)
        elif goal_name == 'contri':
            goal = Congruent(*args)
    
    return goal


def parse_texts_from_file(file_name):
    with open(file_name, "r") as f:
        lines = f.readlines()
    
    texts = [lines[i].strip() for i in range(1, len(lines), 2)]
    return texts
            