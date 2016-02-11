from copy import deepcopy

"""
  Kostas Kopanidis p3130098
  Xrusa Mauraki p3130128
  Lefteris Xatziarapis p3130255
 """


# Extract any sort of entity given its starting and ending token and replacement mark
def sentence_parse(sentence, start, end, mark):
    tokens = sentence.split(',')
    cleared = ""
    found = 0
    results = []
    i = 0
    for token in tokens:
        if found == 0:
            if not token.__contains__(start):
                cleared += token + ","
            elif token.__contains__(start) and token.__contains__(end):
                results.append(token)
                cleared += mark + ","
                i += 1
            else:
                results.append(token)
                found += 1
        else:
            results[i] += "," + token
            if token.__contains__(end):
                if found > 1:
                    found -= 1
                else:
                    cleared += mark + ","
                    found = 0
                    i += 1
            elif token.__contains__(start):
                found += 1

    return results, cleared


# Extract fact from string
def extract_facts(sentence):
    facts, cleared = sentence_parse(sentence, '(', ')', "!-!")
    formatted_facts = []
    for fact in facts:
        name = fact[0:fact.index("(")]
        attr = fact[fact.index("(") + 1:fact.rfind(")")]
        formatted_facts.append(KnowledgeBase.Fact(name, attr))
    return_val = KnowledgeBase.Extractor(formatted_facts, cleared)
    return return_val


# Extract a list from a string
def extract_list(sentence):
    facts, cleared = sentence_parse(sentence, '[', ']', "@-@")
    lists = None
    if len(facts) == 0:
        return None, None
    for fact in facts:
        fact = fact[fact.index('[') + 1:fact.rfind(']')]
        res, parsed = extract_list(fact)
        result = []
        delimiter = ','
        if res is None:
            data = fact
        else:
            data = parsed
        if data.__contains__('|'):
            delimiter = '|'
        if lists is None:
            lists = []
        for atr in data.split(delimiter):
            if atr == "":
                continue
            if res is not None and atr == "@-@":
                result.append(res.pop(0))
            elif atr[0].isupper():
                result.append(KnowledgeBase.Attribute(atr, "var"))
            else:
                result.append(KnowledgeBase.Attribute(atr, "atom"))
        if delimiter == '|':
            result[1].name = '|' + result[1].name
        lists.append(result)
    return lists, cleared


# Replaces facts inside lists
def replace_facts(list_a, functions):
    for item in list_a:
        if isinstance(item, list):
            replace_facts(item, functions)
        elif item == "!-!":
            list_a[list_a.index(item)] = functions.pop(0)


# The Knowledge Base does not account for the existence of ';'
class KnowledgeBase:
    # A class used as a "bundle" return
    # Clearly not that needed now, it used to be necessary now it's a decoration
    # It also has a cool name
    class Extractor:
        def __init__(self, facts, sentence):
            self.facts = facts
            self.sentence = sentence

    class Attribute:
        def __init__(self, attr, attr_type):
            self.name = attr
            self.attr_type = attr_type

    class Fact:
        """
            Step 1:Check if there may be facts embedded in the fact, and try to extract them
            Step 2:Check if there may be lists and repeat the above
            Step 3:For every attribute in the attribute string, check if there is the !-! operator which indicates
             extracted fact or @-@ which indicates extracted list, and replace it accordingly. For the lists,
             we double check if themselves contain facts
            Step 4:Categorize all attributes as either var or atom. This step is obviously skipped for facts and lists
        """

        def __init__(self, name, attribute):
            self.name = name
            self.attr = []
            extract, lists = None, None
            if not isinstance(attribute, list):
                if attribute.__contains__('('):
                    extract = extract_facts(attribute)
                    attribute = extract.sentence
                if attribute.__contains__('['):
                    lists, attribute = extract_list(attribute)
                for atr in attribute.split(','):
                    if atr == "":
                        continue
                    elif atr == "!-!":
                        self.attr.append(extract.facts.pop(0))
                    elif atr == "@-@" and lists is not None:
                        self.attr.append(lists.pop(0))
                        if extract is not None:
                            replace_facts(self.attr[len(self.attr) - 1], extract.facts)
                    elif atr[0].isupper():
                        self.attr.append(KnowledgeBase.Attribute(atr, "var"))
                    else:
                        self.attr.append(KnowledgeBase.Attribute(atr, "atom"))
            else:
                self.attr = attribute

    # The Rule entity class
    class Rule:
        """
            Step 1:Check if there may be facts embedded in the rule, and try to extract them
            Step 2:Check if there may be lists and repeat the above
            Step 3:For every attribute in the attribute string, check if there is the !-! operator which indicates
             extracted fact or @-@ which indicates extracted list, and replace it accordingly. For the lists,
             we double check if themselves contain facts
            Step 4:Categorize all attributes as either var or atom. This step is obviously skipped for facts and lists
            Step 5:Extract all the facts necessary for the rule to be valid
        """

        def __init__(self, name, attribute, facts):
            self.name = name
            self.attr = []
            extract, lists = None, None
            if attribute.__contains__('('):
                extract = extract_facts(attribute)
                attribute = extract.sentence
            if attribute.__contains__('['):
                lists, attribute = extract_list(attribute)
            for atr in attribute.split(','):
                if atr == "":
                    continue
                elif atr == "!-!":
                    self.attr.append(extract.facts.pop(0))
                elif atr == "@-@" and lists is not None:
                    self.attr.append(lists.pop(0))
                    if extract is not None:
                        replace_facts(self.attr[len(self.attr) - 1], extract.facts)
                elif atr[0].isupper():
                    self.attr.append(KnowledgeBase.Attribute(atr, "var"))
                else:
                    self.attr.append(KnowledgeBase.Attribute(atr, "atom"))
            self.fact = extract_facts(facts).facts

    class Unifier:

        def __init__(self):
            self.__status = True
            self.varsToTerms = dict()

        # If the prolog list symbol is contained remove it before assigning a key
        def add_unification(self, var, term):
            copy = deepcopy(var)
            if var.name.__contains__('|'):
                copy.name = copy.name[1:]
            self.varsToTerms[copy] = term

        # Search for keys removing the list indicator if present
        def has(self, item):
            if isinstance(item, list):
                return False
            comparator = item.name
            if item.name.__contains__('|'):
                comparator = comparator[1:]
            for key in self.varsToTerms:
                if key.name == comparator:
                    return True

        # Get the term of key removing the list operator as above
        def get_term(self, term):
            comparator = term.name
            if term.name.__contains__('|'):
                comparator = comparator[1:]
            for key in self.varsToTerms:
                if key.name == comparator:
                    return self.varsToTerms[key]

        # Make a copy of the unifier, shallow copy could be used also, this seemed faster
        def copy(self):
            copy = KnowledgeBase.Unifier()
            for key in self.varsToTerms.keys():
                copy.varsToTerms[key] = self.varsToTerms[key]
            return copy

    # Parse the file and pre-process the extracted the data
    def __init__(self, filename):
        self.filename = filename
        if not filename.endswith(".pl"):
            self.opened = False
            return
        file = open(filename)
        if file:
            self.facts = []
            self.rules = []
            self.opened = self.populate_kb(file.read().replace('\n', '').replace(' ', '').split('.'))
        else:
            self.opened = False

    # Given a "text" array which contains statements identify the probable type of each one
    # then try to extract an entity
    def populate_kb(self, text):
        for line in text:
            if line == '':
                break
            if not line.__contains__(":-"):
                if not self.add_fact(line):
                    return False
            elif line.__contains__(":-"):
                if not self.add_rule(line):
                    return False
            else:
                return False
        if self.rules.__sizeof__() == 0 and self.facts.__sizeof__() == 0:
            return False
        return True

    # Same as the one below but for rules
    def add_rule(self, rule):
        name = rule[0:rule.index("(")]
        attr = rule[rule.index("(") + 1:rule.rfind(":-") - 1]
        self.rules.append(self.Rule(name, attr, rule[rule.index(":-") + 2:]))
        return True

    # Cut the string at the LAST closing parenthesis
    def add_fact(self, fact):
        name = fact[0:fact.index("(")]
        attr = fact[fact.index("(") + 1:fact.rfind(")")]
        self.facts.append(self.Fact(name, attr))
        return True
