from mal_types import AtomType, AtomAtom, BooleanAtom, IntAtom, ListAtom, ListLikeAtom, NilAtom, StringAtom
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
}
