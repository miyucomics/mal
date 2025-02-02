import readline

def READ(arg):
    return arg

def EVAL(arg):
    return arg

def PRINT(arg):
    return arg

def rep(arg):
    ast = READ(arg)
    result = EVAL(ast)
    return PRINT(result)

readline.set_auto_history(True)
while True:
    print(rep(input("user> ")))
