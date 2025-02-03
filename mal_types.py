from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

class AtomType(Enum):
    ATOM = auto()
    BOOLEAN = auto()
    FUNCTION = auto()
    INT = auto()
    KEYWORD = auto()
    LIST = auto()
    MAP = auto()
    NIL = auto()
    STRING = auto()
    SYMBOL = auto()
    VECTOR = auto()

class Atom:
    def type(self) -> AtomType:
        raise NotImplementedError()

    def truthy(self) -> bool:
        return True

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Atom):
            return False
        return self.type() == other.type() and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.type(), self.value))

    def __str__(self) -> str:
        raise NotImplementedError()

@dataclass
class AtomAtom(Atom):
    value: Atom

    def type(self) -> AtomType:
        return AtomType.ATOM

    def truthy(self) -> bool:
        return self.value.truthy()

    def __str__(self) -> str:
        return f"(atom {self.value})"

class NilAtom(Atom):
    value = None

    def type(self) -> AtomType:
        return AtomType.NIL

    def truthy(self) -> bool:
        return False

    def __str__(self) -> str:
        return "nil"

@dataclass
class BooleanAtom(Atom):
    value: bool

    def truthy(self) -> bool:
        return self.value

    def type(self) -> AtomType:
        return AtomType.BOOLEAN

    def __str__(self) -> str:
        return "true" if self.value else "false"

@dataclass(frozen=True)
class IntAtom(Atom):
    value: int

    def type(self) -> AtomType:
        return AtomType.INT

    def __str__(self) -> str:
        return str(self.value)

@dataclass(frozen=True)
class SymbolAtom(Atom):
    value: str

    def type(self) -> AtomType:
        return AtomType.SYMBOL

    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class StringAtom(Atom):
    value: str

    def type(self) -> AtomType:
        return AtomType.STRING

@dataclass(frozen=True)
class KeywordAtom(Atom):
    value: str

    def type(self) -> AtomType:
        return AtomType.KEYWORD

    def __str__(self) -> str:
        return f':{self.value[1:]}'

@dataclass
class FunctionAtom(Atom):
    value: Any

    def type(self) -> AtomType:
        return AtomType.FUNCTION

    def __str__(self) -> str:
        return "#<function>"

@dataclass
class MapAtom(Atom):
    value: dict[Atom, Atom] = None

    def __post_init__(self):
        self.value = self.value or {}

    def type(self) -> AtomType:
        return AtomType.MAP

    def push(self, key: Atom, value: Atom):
        if not isinstance(key, (KeywordAtom, IntAtom, StringAtom, SymbolAtom)):
            raise TypeError(f"Unhashable key type: {type(key).__name__}")
        self.value[key] = value

class ListLikeAtom(Atom):
    def as_list(self) -> list:
        return self.value

@dataclass
class ListAtom(ListLikeAtom):
    value: list[Atom] = None

    def __post_init__(self):
        self.value = self.value or []

    def type(self) -> AtomType:
        return AtomType.LIST

    def push(self, iota: Atom):
        self.value.append(iota)

@dataclass
class VectorAtom(ListLikeAtom):
    value: list[Atom] = None

    def __post_init__(self):
        self.value = self.value or []

    def type(self) -> AtomType:
        return AtomType.VECTOR

    def push(self, iota: Atom):
        self.value.append(iota)
