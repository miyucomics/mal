import readline
from reader import read_str
from printer import pr_str

def rep(arg):
    ast = read_str(arg)
    return pr_str(ast, True)

readline.set_auto_history(True)
while True:
    try:
        result = rep(input("user> "))
    except EOFError:
        print("EOF")
    else:
        print(result)
