import readline
from reader import read_str
from printer import pr_str
from os.path import exists

if exists("./history.txt"):
    readline.read_history_file("./history.txt")

def rep(arg):
    ast = read_str(arg)
    return pr_str(ast, True)

readline.set_auto_history(True)
while True:
    try:
        result = rep(input("user> "))
        readline.write_history_file("./history.txt")
    except EOFError:
        print("EOF")
    else:
        print(result)
