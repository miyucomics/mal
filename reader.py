from mal_types import BooleanAtom, IntAtom, KeywordAtom, ListAtom, MapAtom, NilAtom, StringAtom, SymbolAtom, VectorAtom

string_contractions = {
    "\\n": "\n",
    '\\"': '"',
    "\\\\": "\\",
}

def read_str(code: str):
    tokens = tokenize(code)
    reader = Reader(tokens)
    return read_form(reader)

class Reader:
    tokens: list[str]
    position: int

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def peek(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def next(self):
        if self.position < len(self.tokens):
            self.position += 1
            return self.tokens[self.position - 1]
        return None

def tokenize(code: str):
    position = 0
    tokens = []
    ignore = "\t\r\n, "
    special_chars = "[]{}()'`~^@"
    while position < len(code):
        char = code[position]

        if char in ignore:
            position += 1
            continue

        if char == "~" and position < len(code) - 1 and code[position + 1] == "@":
            tokens.append("~@")
            position += 2
            continue

        if char in special_chars:
            tokens.append(char)
            position += 1
            continue

        if char == '"':
            token = ''
            position += 1
            while position < len(code):
                new_char = code[position]
                if new_char == "\\":
                    token += string_contractions[code[position:position + 2]]
                    position += 2
                    continue
                if new_char == '"':
                    position += 1
                    break
                token += new_char
                position += 1
            else:
                raise EOFError()
            tokens.append(f'"{token}"')

        if char == ';':
            token = ';'
            position += 1
            while position < len(code):
                new_char = code[position]
                token += new_char
                position += 1
            tokens.append(token)

        token = ""
        while position < len(code):
            char = code[position]
            if char in special_chars or char.isspace():
                position -= 1
                break
            if char not in ignore:
                token += char
            position += 1
        if token != "":
            tokens.append(token)

        position += 1

    return tokens

def read_form(reader: Reader):
    token = reader.peek()
    if token is None:
        raise EOFError()
    match token:
        case "^": return read_with_meta(reader)
        case "'": return read_quotelike(reader, "quote")
        case "`": return read_quotelike(reader, "quasiquote")
        case "~": return read_quotelike(reader, "unquote")
        case "@": return read_quotelike(reader, "deref")
        case "~@": return read_quotelike(reader, "splice-unquote")
        case "{": return read_hashmap(reader)
        case "(": return read_listlike(reader, ")", ListAtom)
        case "[": return read_listlike(reader, "]", VectorAtom)
        case _: return read_atom(reader)

def read_with_meta(reader):
    holder = ListAtom()
    holder.push(SymbolAtom("with-meta"))
    reader.next()
    a = read_form(reader)
    b = read_form(reader)
    holder.push(b)
    holder.push(a)
    return holder

def read_quotelike(reader, name):
    holder = ListAtom()
    holder.push(SymbolAtom(name))
    reader.next()
    holder.push(read_form(reader))
    return holder

def read_hashmap(reader: Reader):
    reader.next()
    mapAtom = MapAtom()
    while token := reader.peek():
        if token == "}":
            reader.next()
            return mapAtom
        key = read_form(reader)
        value = read_form(reader)
        mapAtom.push(key, value)
    raise EOFError()

def read_listlike(reader: Reader, closing, constructor):
    reader.next()
    holder = constructor()
    while token := reader.peek():
        if token == closing:
            reader.next()
            return holder
        holder.push(read_form(reader))
    raise EOFError()

simple_tokens = {
    "nil": lambda: NilAtom(),
    "false": lambda: BooleanAtom(False),
    "true": lambda: BooleanAtom(True)
}

def read_atom(reader: Reader):
    token = reader.next()
    if token in simple_tokens:
        return simple_tokens[token]()
    if token.startswith('"') and token.endswith('"'):
        return StringAtom(token[1:-1])
    if token.isdigit() or (token[0] == "-" and token[1:].isdigit()):
        return IntAtom(int(token))
    if token.startswith(":"):
        return KeywordAtom("\u029E" + token[1:])
    return SymbolAtom(token)
