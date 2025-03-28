from pyeuclid.formalization.relation import *
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.utils import is_float


def translate_from_ddar(text):
    parts = text.split(' ? ')
    constructions_text_list = parts[0].split('; ')
    query_text = parts[1] if len(parts) > 1 else None
    
    constructions_list = []
    
    for constructions_text in constructions_text_list:
        constructions_text = constructions_text.split(' = ')[1]
        construction_text_list = constructions_text.split(', ')
        constructions = []
        for construction_text in construction_text_list:
            construction_text = construction_text.split(' ')
            rule_name = construction_text[0]
            arg_names = [name.replace('_', '') for name in construction_text[1:]]
            rule = globals()['construct_'+rule_name]
            args = [float(arg_name) if is_float(arg_name) else Point(arg_name) for arg_name in arg_names]
            construction = rule(*args)
            constructions.append(construction)
        constructions_list.append(constructions)
    
    return constructions_list
    

def translate_from_file(file_name):
    with open(file_name, "r") as f:
        lines = f.readlines()
    
    texts = [lines[i].strip() for i in range(1, len(lines), 2)]
    return texts
            