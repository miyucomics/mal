import readline
from reader import read_str
from printer import pr_str
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

def eval_def(data, env):
    value = eval(data[2], repl_env)
    repl_env.set(data[1], value)
    return value

def eval_let(data, env):
    new_env = Env(env)
    binds = data[1].value
    for i in range(len(binds) // 2):
        new_env.set(binds[i * 2], eval(binds[i * 2 + 1], new_env))
    return eval(data[2], new_env)

special_forms = {
    "def!": eval_def,
    "let*": eval_let
}

def eval(ast, env):
    if "DEBUG-EVAL" in env.data:
        state = env.data["DEBUG-EVAL"]
        if state.truthy():
            print("EVAL:", pr_str(ast, True))

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
        data = ast.value
        if len(data) == 0:
            return ast
        if isinstance(data[0], SymbolAtom) and data[0].value in special_forms:
            return special_forms[data[0].value](data, env)

        new = [eval(item, env) for item in data]
        op = new[0]
        assert op.type() == AtomType.FUNCTION, "First item of list should be valid symbol"
        return op.value(new[1:])
    else:
        return ast

def rep(arg):
    ast = read_str(arg)
    result = eval(ast, repl_env)
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
