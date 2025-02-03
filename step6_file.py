import readline
from reader import read_str
from printer import pr_str
from mal_types import AtomType, FunctionAtom, ListAtom, MapAtom, NilAtom, SymbolAtom, VectorAtom
from core import core
from env import Env
from os.path import exists
import sys

if exists("./history.txt"):
    readline.read_history_file("./history.txt")

repl_env = Env()
for key, value in core.items():
    repl_env.set(SymbolAtom(key), FunctionAtom(value))
repl_env.set(SymbolAtom('*ARGV*'), ListAtom(sys.argv[2:]))

def eval_def(ast, env):
    data = ast.value
    value = EVAL(data[2], repl_env)
    repl_env.set(data[1], value)
    return ast, env, value

def eval_let(ast, env):
    data = ast.value
    new_env = Env(env)
    binds = data[1].value
    for i in range(len(binds) // 2):
        new_env.set(binds[i * 2], EVAL(binds[i * 2 + 1], new_env))
    return data[2], new_env, None

def eval_do(ast, env):
    data = ast.value
    for i in range(1, len(data) - 1):
        EVAL(data[i], env)
    return data[-1], env, None

def eval_if(ast, env):
    data = ast.value
    cond = EVAL(data[1], env)
    if cond.type() == AtomType.NIL or cond.value is False:
        if len(data) > 3:
            return data[3], env, None
        return NilAtom(), env, None
    return data[2], env, None

def eval_fn(ast, env):
    data = ast.value
    return ast, env, {
        "ast": data[2],
        "params": data[1].value,
        "env": env,
        "fn": FunctionAtom(lambda args: EVAL(data[2], Env(env, data[1].value, args)))
    }

special_forms = {
    "def!": eval_def,
    "let*": eval_let,
    "do": eval_do,
    "if": eval_if,
    "fn*": eval_fn,
}

def EVAL(ast, env):
    while True:
        if "DEBUG-EVAL" in env.data:
            state = env.data["DEBUG-EVAL"]
            if state.truthy():
                print("EVAL:", pr_str(ast, True))

        if ast.type() == AtomType.SYMBOL:
            return env.get(ast)
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
            data = ast.value
            if len(data) == 0:
                return ast
            if isinstance(data[0], SymbolAtom) and data[0].value in special_forms:
                ast, env, return_value = special_forms[data[0].value](ast, env)
                if return_value is None:
                    continue
                return return_value

            new = [EVAL(item, env) for item in data]
            op = new[0]
            if type(op) is dict:
                ast = op["ast"]
                env = Env(op["env"], op["params"], new[1:])
                continue
            elif op.type() == AtomType.FUNCTION:
                return op.value(new[1:])
        else:
            return ast

def rep(arg):
    ast = read_str(arg)
    result = EVAL(ast, repl_env)
    return pr_str(result, True)

repl_env.set(SymbolAtom("eval"), FunctionAtom(lambda ast: EVAL(ast[0], repl_env)))
rep('(def! not (fn* (a) (if a false true)))')
rep('(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) "\nnil)")))))')

if len(sys.argv) > 1:
    path = sys.argv[1]
    rep(f'(load-file "{path}")')
    exit()

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
