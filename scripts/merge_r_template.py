import json
from pyeuclid.informalization.relation_template_auto import relation_template as auto_template
from pyeuclid.informalization.relation_template_manual import relation_template as manual_template

auto_list = []
relation_template = {}
for relation in manual_template.keys():
    if relation in auto_template:
        auto_list.append(relation)
        relation_template[relation] = auto_template[relation]
    else:
        relation_template[relation] = manual_template[relation]
    
print(auto_list)
with open("pyeuclid/informalization/relation_template_merge.py", "w") as f:
    f.write("relation_template = " + json.dumps(relation_template, indent=4))
