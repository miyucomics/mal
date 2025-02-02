import readline
from reader import read_str

def READ(arg):
    return read_str(arg)

def EVAL(arg):
    return arg

def PRINT(arg):
    return str(arg)

def rep(arg):
    ast = READ(arg)
    result = EVAL(ast)
    return PRINT(result)

readline.set_auto_history(True)
while True:
    try:
        result = rep(input("user> "))
    except EOFError:
        print("EOF")
    else:
        print(result)
