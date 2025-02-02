from mal_types import MapAtom, ListAtom, StringAtom, VectorAtom

def pr_str(atom, print_readably):
    if isinstance(atom, StringAtom):
        if not print_readably:
            return atom.value
        return f'"{atom.value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')}"'
    elif isinstance(atom, ListAtom):
        return "(" + " ".join(pr_str(item, print_readably) for item in atom.as_list()) + ")"
    elif isinstance(atom, VectorAtom):
        return "[" + " ".join(pr_str(item, print_readably) for item in atom.as_list()) + "]"
    elif isinstance(atom, MapAtom):
        return "{" + " ".join(
            pr_str(key, print_readably) + " " + pr_str(value, print_readably)
            for key, value in atom.value.items()
        ) + "}"
    return str(atom)
