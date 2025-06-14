from mal_types import AtomType, AtomAtom, BooleanAtom, FunctionAtom, IntAtom, ListAtom, ListLikeAtom, NilAtom, StringAtom, VectorAtom, MalException, SymbolAtom, KeywordAtom, MapAtom
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

    if isinstance(a, MapAtom) and isinstance(b, MapAtom):
        if set(a.value.keys()) != set(b.value.keys()):
            return BooleanAtom(False)
        for key in a.value:
            if not equal([a.value[key], b.value[key]]).truthy():
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

def _hash_map(args):
    if len(args) % 2 != 0:
        raise ValueError("hash-map requires even number of arguments")
    map_atom = MapAtom()
    for i in range(0, len(args), 2):
        map_atom.push(args[i], args[i + 1])
    return map_atom

def _assoc(args):
    original = treat_as(get(args, 0), AtomType.MAP)
    map_atom = MapAtom(dict(original))
    rest = args[1:]
    if len(rest) % 2 != 0:
        raise ValueError("assoc requires even number of arguments for key-value pairs after the map")
    for i in range(0, len(rest), 2):
        map_atom.push(rest[i], rest[i + 1])
    return map_atom

def _dissoc(args):
    original = treat_as(get(args, 0), AtomType.MAP)
    map_atom = MapAtom(dict(original))
    for key in args[1:]:
        map_atom.value.pop(key, None)
    return map_atom

def _get(args):
    map_atom = get(args, 0)
    if isinstance(map_atom, NilAtom):
        return NilAtom()
    treat_as(map_atom, AtomType.MAP)
    return map_atom.value.get(get(args, 1), NilAtom())

def _contains(args):
    map_atom = treat_as(get(args, 0), AtomType.MAP)
    return BooleanAtom(get(args, 1) in map_atom)

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

    "throw": mal_throw,
    "nil?": lambda args: BooleanAtom(isinstance(get(args, 0), NilAtom)),
    "true?": lambda args: BooleanAtom(isinstance(get(args, 0), BooleanAtom) and get(args, 0).value is True),
    "false?": lambda args: BooleanAtom(isinstance(get(args, 0), BooleanAtom) and get(args, 0).value is False),
    "symbol?": lambda args: BooleanAtom(isinstance(get(args, 0), SymbolAtom)),
    "symbol": lambda args: SymbolAtom(treat_as(get(args, 0), AtomType.STRING)),
    "keyword": lambda args: get(args, 0) if isinstance(get(args, 0), KeywordAtom) else KeywordAtom("\u029e" + treat_as(get(args, 0), AtomType.STRING)),
    "keyword?": lambda args: BooleanAtom(isinstance(get(args, 0), KeywordAtom)),
    "vector": lambda args: VectorAtom(args[:]),
    "vector?": lambda args: BooleanAtom(isinstance(get(args, 0), VectorAtom)),
    "sequential?": lambda args: BooleanAtom(isinstance(get(args, 0), ListLikeAtom)),
    "hash-map": lambda args: _hash_map(args),
    "map?": lambda args: BooleanAtom(isinstance(get(args, 0), MapAtom)),
    "assoc":       lambda args: _assoc(args),
    "dissoc":      lambda args: _dissoc(args),
    "get":         lambda args: _get(args),
    "contains?":   lambda args: _contains(args),
    "keys":        lambda args: ListAtom(list(get(args, 0).value.keys())),
    "vals":        lambda args: ListAtom(list(get(args, 0).value.values())),
}
