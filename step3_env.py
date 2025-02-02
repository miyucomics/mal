import readline
from reader import read_str
from mal_types import AtomType, FunctionAtom, IntAtom, VectorAtom, MapAtom, SymbolAtom
from env import Env

def biinteger_operation(args, op):
    assert len(args) == 2
    a = args[0]
    b = args[1]
    assert a.type() == AtomType.INT
    assert b.type() == AtomType.INT
    return IntAtom(op(a.value, b.value))

repl_env = Env()
repl_env.set(SymbolAtom("+"), FunctionAtom(lambda args: biinteger_operation(args, lambda a, b: a + b)))
repl_env.set(SymbolAtom("-"), FunctionAtom(lambda args: biinteger_operation(args, lambda a, b: a - b)))
repl_env.set(SymbolAtom("*"), FunctionAtom(lambda args: biinteger_operation(args, lambda a, b: a * b)))
repl_env.set(SymbolAtom("/"), FunctionAtom(lambda args: biinteger_operation(args, lambda a, b: a // b)))

def eval(ast, env):
    if "DEBUG-EVAL" in env.data:
        state = env.data["DEBUG-EVAL"]
        if state.truthy():
            print("EVAL:", ast)

    if ast.type() == AtomType.SYMBOL:
        return env.get(ast)
    elif ast.type() == AtomType.VECTOR:
        new = VectorAtom()
        new.value = [eval(item, env) for item in ast.value]
        return new
    elif ast.type() == AtomType.MAP:
        new = MapAtom()
        for key, value in ast.value.items():
            new.value[key] = eval(value, env)
        return new
    elif ast.type() == AtomType.LIST:
        if len(ast.value) == 0:
            return ast

        if ast.value[0].value == "def!":
            value = eval(ast.value[2], repl_env)
            repl_env.set(ast.value[1], value)
            return value

        if ast.value[0].value == "let*":
            new_env = Env(env)
            binds = ast.value[1].value
            for i in range(len(binds) // 2):
                new_env.set(binds[i * 2], eval(binds[i * 2 + 1], new_env))
            return eval(ast.value[2], new_env)

        new = [eval(item, env) for item in ast.value]
        op = new[0]
        assert op.type() == AtomType.FUNCTION, "First item of list should be valid symbol"
        return op.value(new[1:])
    else:
        return ast

def rep(arg):
    ast = read_str(arg)
    result = eval(ast, repl_env)
    return str(result)

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
