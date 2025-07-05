import readline
from reader import read_str
from printer import pr_str
from mal_types import AtomType, FunctionAtom, ListAtom, MapAtom, NilAtom, SymbolAtom, VectorAtom, StringAtom, ListLikeAtom, MalException
from core import core, get
from env import Env
from os.path import exists
import sys

if exists("./history.txt"):
    readline.read_history_file("./history.txt")

repl_env = Env()
for key, value in core.items():
    repl_env.set(SymbolAtom(key), FunctionAtom(value))
env_args = ListAtom()
for arg in sys.argv[2:]:
    env_args.push(StringAtom(arg))
repl_env.set(SymbolAtom('*ARGV*'), env_args)

def eval_def(ast, env):
    data = ast.value
    value = EVAL(data[2], env)
    env.set(data[1], value)
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

def eval_quote(ast, env):
    return ast, env, ast.value[1]

def quasiquote(ast):
    if isinstance(ast, ListAtom) and len(ast.value) > 0:
        if isinstance(ast.value[0], SymbolAtom) and ast.value[0].value == "unquote":
            return ast.value[1]

    if isinstance(ast, ListLikeAtom):
        result = ListAtom()
        for element in reversed(ast.value):
            if isinstance(element, ListAtom) and len(element.value) > 0:
                if isinstance(element.value[0], SymbolAtom) and element.value[0].value == "splice-unquote":
                    result = ListAtom([SymbolAtom("concat"), element.value[1], result])
                    continue
            result = ListAtom([SymbolAtom("cons"), quasiquote(element), result])

        if isinstance(ast, VectorAtom):
            return ListAtom([SymbolAtom("vec"), result])

        return result

    if isinstance(ast, (SymbolAtom, MapAtom)):
        return ListAtom([SymbolAtom("quote"), ast])

    return ast

def eval_quasiquote(ast, env):
    return quasiquote(ast.value[1]), env, None

def eval_defmacro(ast, env):
    data = ast.value
    value = EVAL(data[2], env)
    if isinstance(value, FunctionAtom):
        value = FunctionAtom(value.value, is_macro=True)
    elif type(value) is dict:
        value = {**value, "is_macro": True}
    env.set(data[1], value)
    return ast, env, value

def eval_try(ast, env):
    data = ast.value
    has_catch = len(data) > 2

    try:
        return ast, env, EVAL(data[1], env)
    except MalException as e:
        if not has_catch:
            raise
        exception = e.value
    except BaseException as e:
        if not has_catch:
            raise
        exception = StringAtom(str(e))

    catch = data[2].value
    catch_env = Env(env, [catch[1]], [exception])
    return catch[2], catch_env, None

special_forms = {
    "def!": eval_def,
    "let*": eval_let,
    "do": eval_do,
    "if": eval_if,
    "fn*": eval_fn,
    "quote": eval_quote,
    "quasiquote": eval_quasiquote,
    "defmacro!": eval_defmacro,
    "try*": eval_try,
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

            op = EVAL(data[0], env)
            if (isinstance(op, FunctionAtom) and op.is_macro) or (type(op) is dict and op.get("is_macro")):
                if type(op) is dict:
                    ast = op["fn"].value(data[1:])
                else:
                    ast = op.value(data[1:])
                continue

            if type(op) is dict:
                new_args = [EVAL(item, env) for item in data[1:]]
                ast = op["ast"]
                env = Env(op["env"], op["params"], new_args)
                continue
            elif op.type() == AtomType.FUNCTION:
                new_args = [EVAL(item, env) for item in data[1:]]
                return op.value(new_args)
        else:
            return ast

def rep(arg):
    ast = read_str(arg)
    result = EVAL(ast, repl_env)
    return pr_str(result, True)

def _apply(args):
    fn = get(args, 0)
    last = get(args, -1)
    middle = args[1:-1]
    full_args = middle + last.as_list()
    if type(fn) is dict:
        return EVAL(fn["ast"], Env(fn["env"], fn["params"], full_args))
    return fn.value(full_args)

def _map(args):
    fn = get(args, 0)
    sequence = get(args, 1)
    result = []
    for item in sequence.as_list():
        if type(fn) is dict:
            result.append(EVAL(fn["ast"], Env(fn["env"], fn["params"], [item])))
        else:
            result.append(fn.value([item]))
    return ListAtom(result)

repl_env.set(SymbolAtom("eval"), FunctionAtom(lambda ast: EVAL(ast[0], repl_env)))
repl_env.set(SymbolAtom("apply"), FunctionAtom(lambda args: _apply(args)))
repl_env.set(SymbolAtom("map"), FunctionAtom(lambda args: _map(args)))
repl_env.set(SymbolAtom("*host-language*"), StringAtom("miyu"))

rep('(def! not (fn* (a) (if a false true)))')
rep('(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) "\nnil)")))))')
rep("(defmacro! cond (fn* (& xs) (if (> (count xs) 0) (list 'if (first xs) (if (> (count xs) 1) (nth xs 1) (throw \"odd number of forms to cond\")) (cons 'cond (rest (rest xs)))))))")

if len(sys.argv) > 1:
    path = sys.argv[1]
    rep(f'(load-file "{path}")')
    exit()
else:
    rep('(println (str "Mal [" *host-language* "]"))')

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
    except MalException as error:
        print("Error:", pr_str(error, True))
    else:
        print(result)
