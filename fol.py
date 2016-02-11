import random

from KB import KnowledgeBase


# An exact copy of the fol-bc-ask algorithm from aima
def fol_bc_ask(kb, goals, unifier):
    if len(goals) == 0:
        return [unifier]
    b_n = subst(unifier, goals[0])
    answers = []
    clauses = kb.facts + kb.rules
    for r in clauses:
        new_vars(r)
        b = r
        unifier_n = unify(b, b_n, unifier)
        if unifier_n is None:
            continue
        if isinstance(r, KnowledgeBase.Rule):
            goals = r.fact + goals[1:]
        else:
            goals = goals[1:]
        answer = fol_bc_ask(kb, goals, compose(unifier_n, unifier))
        if answer is not None:
            answers.extend([uni for uni in answer
                            if not answers.__contains__(uni)])
    return answers


# An exact copy of the unify algorithm from aima
def unify(first, second, u):
    if u is None:
        return None
    if compare(first, second):
        return u
    if variable(first):
        return unify_var(first, second, u)
    elif variable(second):
        return unify_var(second, first, u)
    elif compound(first) and compound(second):
        return unify(first.attr, second.attr, unify(first.name, second.name, u))
    elif is_list(first) and is_list(second):
        list_data = list_check(first, second)
        if list_data is not None:
            if list_data[0] is None:
                return u
            return unify(list_data[3], list_data[4], unify(list_data[1], list_data[2], u))
        return None
    return None


# An exact copy of the unify_var algorithm from aima
def unify_var(first, second, u):
    if u.has(first):
        return unify(u.get_term(first), second, u)
    elif u.has(second):
        return unify(first, u.get_term(second), u)
    elif occurs(first, second):
        return None
    else:
        copy = u.copy()
        copy.add_unification(first, second)
        return copy


# A copy of the substitute algorithm from aima
def subst(uni, sub):
    if is_list(sub):
        return [subst(uni, xi) for xi in sub]
    elif variable(sub):
        for key in uni.varsToTerms.keys():
            if key.name == sub.name:
                return uni.varsToTerms[key]
        return sub
    elif atom(sub):
        return sub
    else:
        result = []
        for arg in sub.attr:
            result.append(subst(uni, arg))
        return KnowledgeBase.Fact(sub.name, result)


# Check if the first occurs in the second
def occurs(first, second):
    if compound(second):
        return second.attr.__contains__(first)
    elif variable(second):
        return first == second
    return False


def variable(argument):
    return isinstance(argument, KnowledgeBase.Attribute) and argument.attr_type == "var"


def atom(argument):
    return isinstance(argument, KnowledgeBase.Attribute) and argument.attr_type == "atom"


def compound(argument):
    return isinstance(argument, KnowledgeBase.Fact) or isinstance(argument, KnowledgeBase.Rule)


def is_list(argument):
    return isinstance(argument, list)


def compare(arg1, arg2):
    if isinstance(arg1, list) and isinstance(arg2, list) and len(arg1) == len(arg2) == 0:
        return True
    if isinstance(arg1, KnowledgeBase.Attribute) and isinstance(arg2, KnowledgeBase.Attribute):
        if arg1.name == arg2.name and arg1.attr_type == arg2.attr_type:
            return True
    elif isinstance(arg1, KnowledgeBase.Fact) and isinstance(arg2, KnowledgeBase.Fact):
        size = len(arg1.attr)
        if arg1.name == arg2.name and size == len(arg2.attr):
            for i in range(size):
                if not compare(arg1.attr[i], arg2.attr[i]):
                    return False
            return True
    elif isinstance(arg1, str) and isinstance(arg2, str):
        if arg1 == arg2:
            return True
    return False


# make the vars "new" by adding a number or increasing the existing one
def new_vars(term, move_by=None):
    if move_by is None:
        move_by = random.randint(1, random.randint(5, 100))
    for attribute in term.attr:
        if isinstance(attribute, KnowledgeBase.Fact):
            new_vars(attribute, move_by)
            continue
        if isinstance(attribute, list):
            new_vars_lists(attribute, move_by)
            continue
        if attribute.attr_type == "atom":
            continue
        attr = attribute.name
        if attr[len(attr) - 1].isdigit():
            attr = attr[:len(attr) - 1] + str(int(attr[len(attr) - 1]) + move_by)
        else:
            attr += str(move_by)
        term.attr[term.attr.index(attribute)].name = attr
    if isinstance(term, KnowledgeBase.Rule):
        for i in range(len(term.fact)):
            new_vars(term.fact[i], move_by)


def new_vars_lists(list_a, move_by):
    for item in list_a:
        if isinstance(item, list):
            new_vars_lists(item, move_by)
            continue
        if isinstance(item, KnowledgeBase.Fact):
            new_vars(item, move_by)
            continue
        if item.attr_type == "atom":
            continue
        attr = item.name
        if attr[len(attr) - 1].isdigit():
            attr = attr[:len(attr) - 1] + str(int(attr[len(attr) - 1]) + move_by)
        else:
            attr += str(move_by)
        list_a[list_a.index(item)].name = attr


def compose(theta_n, theta):
    unifier = KnowledgeBase.Unifier()
    for key in list(theta_n.varsToTerms.keys()):
        unifier.add_unification(key, subst(theta, theta_n.varsToTerms[key]))

    for key in list(theta.varsToTerms.keys()):
        if not unifier.has(key):
            unifier.add_unification(key, subst(theta_n, theta.varsToTerms[key]))
    return unifier


# Various checks for prolog and python lists
def list_check(list_a, list_b):
    response = []
    length_a = len(list_a)
    length_b = len(list_b)
    if length_a == length_b and \
            not (secondary_check(list_a) or secondary_check(list_b)):
        if length_a == 0:
            response.append(None)
        else:
            response.append(length_a)
            if length_a > 1:
                if length_a - 1 == 1:
                    response.extend([list_a[0], list_b[0]])
                    response.extend([list_a[1], list_b[1]])
                else:
                    response.extend([list_a[0], list_b[0]])
                    response.extend([list_a[1:], list_b[1:]])
            else:
                response.extend([list_a[0], list_b[0]])
                response.extend([[], []])
    else:
        if secondary_check(list_a) and length_b > 0:
            response.append(0.1)
            response.extend(head_extract(list_a, list_b))
            response.extend(tail_extract(list_a, list_b))
        elif secondary_check(list_b) and length_a > 0:
            response.append(0.1)
            response.extend(head_extract(list_b, list_a))
            response.extend(tail_extract(list_b, list_a))
        else:
            return None
    return response


def head_extract(dyn_list, regular_list):
    return [dyn_list[0], regular_list[0]]


def tail_extract(dyn_list, regular_list):
    if len(regular_list) == 1:
        return [dyn_list[1], []]
    elif len(regular_list) > 1:
        return [dyn_list[1], regular_list[1:]]


def secondary_check(list_a):
    return len(list_a) > 1 and not isinstance(list_a[1], list) \
           and list_a[1].name.__contains__('|')
