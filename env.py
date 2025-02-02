from mal_types import SymbolAtom, Atom, ListAtom

class Env:
    def __init__(self, outer=None, binds=None, exprs=None):
        self.outer = outer
        self.data = {}
        if binds is not None:
            for i, bind in enumerate(binds):
                if bind.value == "&":
                    self.set(binds[i + 1], ListAtom(exprs[i:]))
                    break
                self.set(bind, exprs[i])

    def set(self, symbol: SymbolAtom, atom: Atom):
        self.data[symbol.value] = atom

    def get(self, symbol: SymbolAtom):
        if symbol.value not in self.data:
            if self.outer is None:
                raise KeyError(f"'{symbol.value}' not found.")
            return self.outer.get(symbol)
        return self.data[symbol.value]
