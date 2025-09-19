import json
import os
import shutil
from pathlib import Path
import inspect

from pyeuclid.informalization.informalize_utils import *
from pyeuclid.informalization.construction_rule_template import construction_rule_template
from pyeuclid.formalization.construction_rule import construction_rule_sets

prompt = ""
for cr in construction_rule_sets["auxiliary_construction"]:
    methods = inspect.getmembers(cr, predicate=inspect.isfunction)
    out_params = []
    in_params = []
    for name, func in methods:
        sig = inspect.signature(func)
        if name == "construct":
            out_params = [param.split(": ")[0].capitalize() for param in str(sig)[1:-1].split(", ")[1:]]
        if name == "__init__":
            in_params = [param.split(": ")[0].capitalize() for param in str(sig)[1:-1].split(", ")[1:]]
    params = out_params + in_params
    # template = random.choice(construction_rule_template[cr.__name__])
    template = construction_rule_template[cr.__name__][0]
    explanation = template[0].format(*[params[i] for i in template[1]])
    out_params_text = (", ").join(out_params)
    in_params_text = (", ").join(in_params)
    params_text = (" ").join(params)
    explanation = f"construct {out_params_text} such that {explanation}"
    cr_name = "_".join(cr.__name__.split("_")[1:])
    prompt += f"{out_params_text} = {cr_name} {params_text}: {explanation}\n"

print(prompt)
with open("scripts_temp/prompt_ag_aux_cons.txt", "w") as f:
    f.write(prompt)
