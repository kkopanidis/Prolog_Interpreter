import KB
import fol

"""
  Kostas Kopanidis p3130098
  Xrusa Mauraki p3130128
  Lefteris Xatziarapis p3130255
 """


# Used to extract the unification for printing
# Iterates through the keys unified searching for keys that match the arguments given
def extract(query, answer):
    printing = ""
    for key in answer.varsToTerms.keys():
        for term in query.attr:
            if not (isinstance(term, list)):
                if term.name == key.name:
                    if isinstance(answer.varsToTerms[key], list):
                        printing += term.name + "["
                        for item in answer.varsToTerms[key]:
                            printing += item.name + ","
                        printing += "] "
                        continue
                    printing += term.name + ":" + answer.varsToTerms[key].name + " "
    return printing


# Break down the argument given and query the KB through the fol algorithm
# For each unifier returned try to extract an answer
def evaluate(command):
    command = command.replace('\n', '').replace(' ', '')
    name = command[0:command.index("(")]
    attr = command[command.index("(") + 1:command.rfind(")")]
    query = KB.KnowledgeBase.Fact(name, attr)
    unifier = KB.KnowledgeBase.Unifier()
    answer = fol.fol_bc_ask(kb, [query], unifier)
    if answer is None or len(answer) == 0 or answer[0] is None:
        print("No valid unification found")
    elif answer is [] or len(answer[0].varsToTerms) == 0:
        print("True")
    else:
        printable = ""
        for ans in answer:
            printable += "{"
            printable += extract(query, ans)
            printable += "}\n"
        if len(printable) > 1:
            print("True for:\n" + printable)
        else:
            print(True)


kb = KB.KnowledgeBase(input("Prolog filename: "))
if kb.opened:
    while True:
        argument = input("Type a command to evaluate or exit to close\n> ")
        if argument == "exit":
            break
        else:
            try:
                evaluate(argument)
            except:
                print("Something went terribly wrong")
else:
    print("File failed to open!exiting")
