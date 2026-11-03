KEYWORDS = {"number", "array", "of", "if", "then", "else", "while", "do", "read", "write"}
OPERATORS = {"==", "!=", "<=", ">=", "+", "-", "*", "/", "=", "<", ">"}
SEPARATORS = {"[", "]", "{", "}", "(", ")", ";"}


class SymbolTable:
    def __init__(self):
        self.table = {}
        self.counter = 0

    def insert(self, value):
        if value not in self.table:
            self.table[value] = self.counter
            self.counter += 1
        return self.table[value]


def scan_identifier(text, start_index):
    """DFA simulation for Identifiers: [a-zA-Z_][a-zA-Z0-9_]*"""
    state = "q0"
    i = start_index
    lexeme = ""

    while i < len(text):
        char = text[i]
        if state == "q0":
            if char.isalpha() or char == '_':
                state = "q1"
                lexeme += char
                i += 1
            else:
                break
        elif state == "q1":
            if char.isalnum() or char == '_':
                lexeme += char
                i += 1
            else:
                break

    if state == "q1":
        return lexeme, i
    return None, start_index


def scan_constant(text, start_index):
    """DFA simulation for Constants: Integer & Float numbers"""
    state = "p0"
    i = start_index
    lexeme = ""

    while i < len(text):
        char = text[i]
        if state == "p0":
            if char.isdigit():
                state = "p1"
                lexeme += char
                i += 1
            else:
                break
        elif state == "p1":
            if char.isdigit():
                lexeme += char
                i += 1
            elif char == '.':
                state = "p2"
                lexeme += char
                i += 1
            else:
                break
        elif state == "p2":
            if char.isdigit():
                state = "p3"
                lexeme += char
                i += 1
            else:
                return None, start_index  # Malformed float like '45.'
        elif state == "p3":
            if char.isdigit():
                lexeme += char
                i += 1
            else:
                break

    if state in ("p1", "p3"):
        return lexeme, i
    return None, start_index


def lexical_analyzer(source_code):
    pif = []
    st = SymbolTable()
    errors = []

    i = 0
    line_num = 1

    while i < len(source_code):
        char = source_code[i]

        if char == '\n':
            line_num += 1
            i += 1
            continue
        if char.isspace():
            i += 1
            continue

        # 1. Check Identifier DFA
        lexeme, next_i = scan_identifier(source_code, i)
        if lexeme:
            if lexeme in KEYWORDS:
                pif.append((lexeme, -1))
            else:
                st_index = st.insert(lexeme)
                pif.append(("id", st_index))
            i = next_i
            continue

        # 2. Check Constant DFA
        lexeme, next_i = scan_constant(source_code, i)
        if lexeme:
            st_index = st.insert(lexeme)
            pif.append(("const", st_index))
            i = next_i
            continue

        # 3. Check Multi-character Operators
        if i + 1 < len(source_code):
            two_char = source_code[i:i + 2]
            if two_char in OPERATORS:
                pif.append((two_char, -1))
                i += 2
                continue

        # 4. Check Single-character Operators & Separators
        if char in OPERATORS or char in SEPARATORS:
            pif.append((char, -1))
            i += 1
            continue

        errors.append(f"Lexical error: unrecognized character '{char}' at line {line_num}")
        i += 1

    return pif, st, errors


if __name__ == "__main__":
    sample_program = """
    number threshold = 45.0;
    read(currentTemp);
    if (currentTemp > threshold) then {
        write(999);
    }
    """

    pif, st, errors = lexical_analyzer(sample_program)

    print("=== PROGRAM INTERNAL FORM (PIF) ===")
    for token, idx in pif:
        print(f"Token: {token:<10} | ST Index: {idx}")

    print("\n=== SYMBOL TABLE (ST) ===")
    for val, idx in sorted(st.table.items(), key=lambda x: x[1]):
        print(f"Index {idx}: {val}")

    if errors:
        print("\n=== ERRORS ===")
        for err in errors:
            print(err)
    else:
        print("\nScanning completed successfully with 0 errors!")
