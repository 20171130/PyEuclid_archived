import random
from pyeuclid.informalization.relation_template import relation_template
from pyeuclid.informalization.construction_rule_template import construction_rule_template

def informalize_construction(construction):
    if " = " in construction and "(" in construction and ")" in construction:
        output, formal_clause = construction.split(" = ")
        output = output.upper().split(",")
        predicate = formal_clause.split("(")[0]
        params = output + formal_clause.split("(")[1].split(")")[0].upper().split(",")
        if predicate in construction_rule_template:
            template = random.choice(construction_rule_template[predicate])
            return output, template[0].format(*[params[i] for i in template[1]])
    return output, formal_clause

def informalize_problem(problem):
    informal_problem = problem
    informal_constructions = []
    problem = problem.split(", ")
    for construction in problem:
        if " = " in construction:
            output, informal_clause = informalize_construction(construction)
            informal_constructions.append([output, informal_clause])
    informal_problem = ", ".join([informal_clause for _, informal_clause in informal_constructions])
    return informal_problem

def informalize_goal(goal):
    informal_goal = informalize_relation(goal)
    # informal_goal = "Please try to prove that:\n" + informal_goal
    return informal_goal

def informalize_aux(aux):
    if aux == "":
        return aux
    informal_aux = aux
    informal_constructions = []
    aux = aux.split(", ")
    for construction in aux:
        if " = " in construction:
            output, informal_clause = informalize_construction(construction)
            informal_constructions.append([output, informal_clause])
    informal_aux = "Construct auxiliary points as follows:\n" + ", ".join(["construct " + ",".join(output) + " such that " + informal_clause for _, informal_clause in informal_constructions])
    return informal_aux

def informalize_term(term):
    if "Angle" in term:
        term_left = term[:term.find("Angle")]
        term_right = term[term.find("Angle") + 11:]
        term = term[term.find("Angle"): term.find("Angle") + 11]
        return term_left + "\u2220" + "".join(term.split("_")[1:]).upper() + term_right
    elif "Length" in term:
        term_left = term[:term.find("Length")]
        term_right = term[term.find("Length") + 10:]
        term = term[term.find("Length"): term.find("Length") + 10]
        return term_left + "".join(term.split("_")[1:]).upper() + term_right
    else:
        return term

def informalize_relation(formal_clause):
    if "(" in formal_clause and ")" in formal_clause:
        predicate = formal_clause.split("(")[0]
        params = formal_clause.split("(")[1].split(")")[0].upper().split(",")
        if predicate in relation_template:
            template = random.choice(relation_template[predicate])
            return template[0].format(*[params[i] for i in template[1]])
    else:
        term_list = "".join(formal_clause.split(" ")).split("-")
        if term_list[0] == "":
            right_list = [term.split("+")[0] for term in term_list[1:]]
            right_list = [informalize_term(term) for term in right_list]
            left_list = [term.split("+")[1:] for term in term_list[1:]]
            left_list = [item for left in left_list for item in left]
            left_list = [informalize_term(term) for term in left_list]
        else:
            right_list = [term.split("+")[0] for term in term_list[1:]]
            right_list = [informalize_term(term) for term in right_list]
            left_list = [term_list[0].split("+")] + [term.split("+")[1:] for term in term_list[1:]]
            left_list = [item for left in left_list for item in left]
            left_list = [informalize_term(term) for term in left_list]
        informal_clause = " + ".join(left_list) + " = " + " + ".join(right_list)
        return informal_clause
    return formal_clause

def informalize_proof_step(proof_step):
    informal = ""
    proof_step = proof_step.split(" => ")
    assert len(proof_step) == 2
    left = proof_step[0]
    right = proof_step[1]
    step_id, left = left.split(". ")
    left_sub_list = left.split(" & ")
    right_sub_list = right.split(" & ")
    left_informal_sub_list = []
    right_informal_sub_list = []
    for left_sub in left_sub_list:
        left_informal_sub_list.append(informalize_relation(left_sub))
    for right_sub in right_sub_list:
        right_informal_sub_list.append(informalize_relation(right_sub))
    left = " and ".join(left_informal_sub_list)
    right = " and ".join(right_informal_sub_list)
    informal = f"Step {step_id}: {left} implies that {right}"
    return informal

def informalize_proof(proof):
    informal_steps = []
    proof = proof.split("\n")
    for proof_step in proof:
        if "=>" in proof_step:
            informal_step = informalize_proof_step(proof_step)
            informal_steps.append(informal_step)
    informal_proof = "\n".join(informal_steps)
    return informal_proof