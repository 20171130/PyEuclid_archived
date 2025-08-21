import json
from pyeuclid.informalization.relation_template_backup import relation_template

keys = relation_template.keys()
for key in keys:
    relation_template[key] = [relation_template[key]]

with open("pyeuclid/informalization/relation_template_manual.py", "w") as f:
    f.write("relation_template = " + json.dumps(relation_template, indent=4))
