import json
from pyeuclid.formalization.construction_rule import construction_rule_sets
from pyeuclid.informalization.pretty_problem_statement_dict import language_dict

missing_rule_list = []
construction_rule_template = {}
for construction_rule_list in construction_rule_sets.values():
    for construction_rule_class in construction_rule_list:
        construction_rule = construction_rule_class.__name__
        key = construction_rule.split("construct_")[-1]
        if key in language_dict:
            informal_list = language_dict[key]
            for informal in informal_list:
                if informal[0][-1] == ".":
                    informal[0] = informal[0][:-1]
                if informal[0][0].isupper():
                    informal[0] = informal[0][0].lower() + informal[0][1:]
            construction_rule_template[construction_rule] = informal_list
        else:
            missing_rule_list.append(construction_rule)

print(missing_rule_list)

with open("pyeuclid/informalization/construction_rule_template_auto.py", "w") as f:
    f.write("construction_rule_template = " + json.dumps(construction_rule_template, indent=4))
