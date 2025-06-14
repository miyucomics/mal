from mal_types import AtomType, AtomAtom, BooleanAtom, FunctionAtom, IntAtom, ListAtom, ListLikeAtom, NilAtom, StringAtom, VectorAtom, MalException
from reader import read_str
from printer import pr_str

def get(args, index):
    if index >= len(args):
        raise ValueError("Not enough arguments.")
    return args[index]

def treat_as(atom, intended_type):
    if atom.type() != intended_type:
        raise ValueError(f"'{atom}' is not of {intended_type}.")
    return atom.value

def biatom_operation(args, op):
    return op(get(args, 0), get(args, 1))

def biinteger_operation(args, op):
    return op(treat_as(get(args, 0), AtomType.INT), treat_as(get(args, 1), AtomType.INT))

def equal(args):
    a, b = get(args, 0), get(args, 1)

    if isinstance(a, ListLikeAtom) and isinstance(b, ListLikeAtom):
        if len(a.as_list()) != len(b.as_list()):
            return BooleanAtom(False)
        for x, y in zip(a.as_list(), b.as_list()):
            if not equal([x, y]).truthy():
                return BooleanAtom(False)
        return BooleanAtom(True)

    if a.type() != b.type():
        return BooleanAtom(False)

    return BooleanAtom(a.value == b.value)

def count(args):
    a = get(args, 0)
    if isinstance(a, ListLikeAtom):
        return IntAtom(len(get(args, 0).as_list()))
    return IntAtom(0)

def empty(args):
    a = get(args, 0)
    if isinstance(a, ListLikeAtom):
        return BooleanAtom(len(get(args, 0).as_list()) == 0)
    return BooleanAtom(False)

def prn(args):
    print(" ".join(pr_str(arg, True) for arg in args))
    return NilAtom()

def println(args):
    print(" ".join(pr_str(arg, False) for arg in args))
    return NilAtom()

def slurp(args):
    filename = treat_as(get(args, 0), AtomType.STRING)
    with open(filename, "r") as file:
        content = file.read()
        return StringAtom(content)
    return NilAtom()

def atom_reset(args):
    atom = get(args, 0)
    treat_as(atom, AtomType.ATOM)
    new = get(args, 1)
    atom.value = new
    return new

def atom_swap(args):
    atom = get(args, 0)
    treat_as(atom, AtomType.ATOM)
    func = get(args, 1)
    if type(func) is dict:
        func = func["fn"]
    new = treat_as(func, AtomType.FUNCTION)([atom.value] + args[2:])
    atom.value = new
    return new

def cons(args):
    head = get(args, 0)
    tail = get(args, 1)
    if isinstance(tail, ListLikeAtom):
        return ListAtom([head] + tail.as_list())
    raise ValueError("cons needs a list as the second argument.")

def concat(args):
    result = []
    for arg in args:
        if isinstance(arg, ListLikeAtom):
            result += arg.as_list()
        else:
            raise ValueError("concat takes only lists for arguments.")
    return ListAtom(result)

def nth(args):
    sequence = get(args, 0)
    index = treat_as(get(args, 1), AtomType.INT)
    if not isinstance(sequence, ListLikeAtom) or index >= len(sequence.as_list()):
        raise ValueError("nth needs a list and an index in range")
    return sequence.as_list()[index]

def first(args):
    sequence = get(args, 0)
    if isinstance(sequence, NilAtom) or (isinstance(sequence, ListLikeAtom) and len(sequence.as_list()) == 0):
        return NilAtom()
    return sequence.as_list()[0]

def rest(args):
    seq = get(args, 0)
    if isinstance(seq, NilAtom) or (isinstance(seq, ListLikeAtom) and len(seq.as_list()) == 0):
        return ListAtom()
    return ListAtom(seq.as_list()[1:])

def mal_throw(args):
    raise MalException(get(args, 0))

core = {
    "+": lambda args: biinteger_operation(args, lambda a, b: IntAtom(a + b)),
    "-": lambda args: biinteger_operation(args, lambda a, b: IntAtom(a - b)),
    "*": lambda args: biinteger_operation(args, lambda a, b: IntAtom(a * b)),
    "/": lambda args: biinteger_operation(args, lambda a, b: IntAtom(a // b)),

    "list": ListAtom,
    "list?": lambda args: BooleanAtom(get(args, 0).type() == AtomType.LIST),
    "empty?": empty,
    "count": count,

    "=": equal,
    "<": lambda args: biinteger_operation(args, lambda a, b: BooleanAtom(a < b)),
    ">": lambda args: biinteger_operation(args, lambda a, b: BooleanAtom(a > b)),
    "<=": lambda args: biinteger_operation(args, lambda a, b: BooleanAtom(a <= b)),
    ">=": lambda args: biinteger_operation(args, lambda a, b: BooleanAtom(a >= b)),

    "prn": prn,
    "pr-str": lambda args: StringAtom(" ".join(pr_str(arg, True) for arg in args)),
    "str": lambda args: StringAtom("".join(pr_str(arg, False) for arg in args)),
    "println": println,

    "read-string": lambda args: read_str(treat_as(get(args, 0), AtomType.STRING)),
    "slurp": slurp,

    "atom": lambda args: AtomAtom(get(args, 0)),
    "atom?": lambda args: BooleanAtom(get(args, 0).type() == AtomType.ATOM),
    "deref": lambda args: treat_as(get(args, 0), AtomType.ATOM),
    "reset!": atom_reset,
    "swap!": atom_swap,

    "cons": cons,
    "concat": concat,
    "vec": lambda args: args[0] if isinstance(args[0], VectorAtom) else VectorAtom(get(args, 0).as_list()[:]),

    "nth": nth,
    "first": first,
    "rest": rest,
    "macro?": lambda args: BooleanAtom(
        (isinstance(get(args, 0), FunctionAtom) and get(args, 0).is_macro) or
        (type(get(args, 0)) is dict and get(args, 0).get("is_macro", False))
    ),

    "throw": mal_throw
}
