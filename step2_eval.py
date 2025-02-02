import readline
from reader import read_str
from printer import pr_str
from mal_types import AtomType, FunctionAtom, IntAtom, VectorAtom, MapAtom

def biinteger_operation(args, op):
    assert len(args) == 2
    a = args[0]
    b = args[1]
    assert a.type() == AtomType.INT
    assert b.type() == AtomType.INT
    return IntAtom(op(a.value, b.value))

repl_env = {
    "+": FunctionAtom(lambda args: biinteger_operation(args, lambda a, b: a + b)),
    "-": FunctionAtom(lambda args: biinteger_operation(args, lambda a, b: a - b)),
    "*": FunctionAtom(lambda args: biinteger_operation(args, lambda a, b: a * b)),
    "/": FunctionAtom(lambda args: biinteger_operation(args, lambda a, b: a // b))
}

def EVAL(ast, env):
    if ast.type() == AtomType.SYMBOL:
        if ast.value in env:
            return env[ast.value]
        raise KeyError("Operation was not found")
    elif ast.type() == AtomType.VECTOR:
        new = VectorAtom()
        new.value = [EVAL(item, env) for item in ast.value]
        return new
    elif ast.type() == AtomType.MAP:
        new = MapAtom()
        for key, value in ast.value.items():
            new.value[key] = EVAL(value, env)
        return new
    elif ast.type() == AtomType.LIST:
        if len(ast.value) == 0:
            return ast
        new = [EVAL(item, env) for item in ast.value]
        op = new[0]
        assert op.type() == AtomType.FUNCTION, "First item of list should be valid symbol"
        return op.value(new[1:])
    else:
        return ast

def rep(arg):
    ast = read_str(arg)
    result = EVAL(ast, repl_env)
    return pr_str(result, True)

readline.set_auto_history(True)
while True:
    try:
        result = rep(input("user> "))
    except EOFError:
        print("EOF")
    except AssertionError as error:
        print(str(error))
    except KeyError as error:
        print(str(error))
    else:
        print(result)
