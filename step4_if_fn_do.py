import readline
from reader import read_str
from mal_types import AtomType, FunctionAtom, MapAtom, NilAtom, SymbolAtom, VectorAtom
from core import core
from env import Env
from os.path import exists

if exists("./history.txt"):
    readline.read_history_file("./history.txt")

repl_env = Env()
for key, value in core.items():
    repl_env.set(SymbolAtom(key), FunctionAtom(value))

def eval(ast, env):
    if "DEBUG-EVAL" in env.data:
        state = env.data["DEBUG-EVAL"]
        if state.value is not False and state.type() != AtomType.NIL:
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
        data = ast.value
        if len(data) == 0:
            return ast

        if data[0].value == "def!":
            value = eval(data[2], repl_env)
            repl_env.set(data[1], value)
            return value

        if data[0].value == "let*":
            new_env = Env(env)
            binds = data[1].value
            for i in range(len(binds) // 2):
                new_env.set(binds[i * 2], eval(binds[i * 2 + 1], new_env))
            return eval(data[2], new_env)

        if data[0].value == "do":
            for i in range(1, len(data) - 1):
                eval(data[i], env)
            return eval(data[-1], env)

        if data[0].value == "if":
            cond = eval(data[1], env)
            if cond.type() == AtomType.NIL or cond.value is False:
                if len(data) > 3:
                    return eval(data[3], env)
                return NilAtom()
            return eval(data[2], env)

        if data[0].value == "fn*":
            return FunctionAtom(lambda args: eval(data[2], Env(env, data[1].value, args)))

        new = [eval(item, env) for item in data]
        op = new[0]
        assert op.type() == AtomType.FUNCTION, "First item of list should be valid symbol"
        return op.value(new[1:])
    else:
        return ast

def rep(arg):
    ast = read_str(arg)
    result = eval(ast, repl_env)
    return str(result)

rep("(def! not (fn* (a) (if a false true)))")

readline.set_auto_history(True)
while True:
    try:
        i = input("user> ")
        readline.write_history_file("./history.txt")
        result = rep(i)
    except EOFError:
        print("EOF")
    except AssertionError as error:
        print(str(error))
    except ValueError as error:
        print(str(error))
    except KeyError as error:
        print(str(error))
    else:
        print(result)
