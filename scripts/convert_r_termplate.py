import json
from pyeuclid.formalization.relation import relations
from pyeuclid.informalization.pretty_problem_statement_dict import language_dict

missing_relation_list = []
relation_template = {}
for relation_class in relations.values():
    relation = relation_class.__name__
    key = relation.lower()
    if key in language_dict:
        informal_list = language_dict[key]
        for informal in informal_list:
            if informal[0][-1] == ".":
                informal[0] = informal[0][:-1]
            if informal[0][0].isupper():
                informal[0] = informal[0][0].lower() + informal[0][1:]
        relation_template[relation] = informal_list
    else:
         missing_relation_list.append(relation)

print(missing_relation_list)

with open("pyeuclid/informalization/relation_template_auto.py", "w") as f:
    f.write("relation_template = " + json.dumps(relation_template, indent=4))
