from pathlib import Path


RESERVEDWORDS = {"image", "array", "pixel", "load", "save", "if", "else", "for", "in", "function", "return", "void", "size", "and", "or"}
OPERATORS = {"==", "!=", "<=", ">=", "+", "-", "*", "/", "=", "<", ">", "and", "or", "&&", "||"}
SEPARATORS = {"[", "]", "{", "}", "(", ")", ",", "."}


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
    """DFA simulation for Identifiers: [a-zA-Z][0-9a-zA-Z]* """
    state = "q0"
    i = start_index
    lexeme = ""

    while i < len(text):
        char = text[i]
        if state == "q0":
            if char.isalpha():
                state = "q1"
                lexeme += char
                i += 1
            else:
                break
        elif state == "q1":
            if char.isalnum():
                lexeme += char
                i += 1
            else:
                break

    if state == "q1":
        return lexeme, i
    return None, start_index


def scan_number(text, start_index):
    """DFA simulation for Numbers: 0|[1-9][0-9]* """
    state = "q0"
    i = start_index
    lexeme = ""

    # while i < len(text):
    #     char = text[i]
    #     if state == "p0":
    #         if char.isdigit():
    #             state = "p1"
    #             lexeme += char
    #             i += 1
    #         else:
    #             break
    #     elif state == "p1":
    #         if char.isdigit():
    #             lexeme += char
    #             i += 1
    #         elif char == '.':
    #             state = "p2"
    #             lexeme += char
    #             i += 1
    #         else:
    #             break
    #     elif state == "p2":
    #         if char.isdigit():
    #             state = "p3"
    #             lexeme += char
    #             i += 1
    #         else:
    #             return None, start_index  # Malformed float like '45.'
    #     elif state == "p3":
    #         if char.isdigit():
    #             lexeme += char
    #             i += 1
    #         else:
    #             break

    while i < len(text):
        char = text[i]
        if state == "q0":
            if char.isdigit():
                if char == "0":
                    state = "q1"
                else:
                    state = "q2"

                lexeme += char
                i += 1
            else:
                break
        elif state == "q1":
            if char.isdigit():
                while i < len(text) and char.isdigit():
                    char = text[i]
                    i += 1

                return None, i - 1 # Malformed number like '01'
            break
        elif state == "q2":
            if char.isdigit():
                lexeme += char
                i += 1
            else:
                break

    if state in ("q1", "q2"):
        return lexeme, i
    return None, start_index


def scan_string(text, start_index):
    """DFA simulation for Strings: \"[^\"\n]*\" """
    state = "q0"
    i = start_index
    lexeme = ""

    while i < len(text):
        char = text[i]
        if state == "q0":
            if char == "\"":
                state = "q1"
                lexeme += char
                i += 1
            else:
                break
        elif state == "q1":
            if char == "\n":
                return None, start_index
            elif char == "\"":
                state = "q2"
            lexeme += char
            i += 1
        elif state == "q2":
            break

    if state == "q2":
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
            if lexeme in RESERVEDWORDS:
                pif.append((lexeme, -1))
            elif lexeme in ["and", "or"]:
                pif.append((lexeme, -1))
            else:
                st_index = st.insert(lexeme)
                pif.append(("id", st_index))
            i = next_i
            continue

        # 2. Check Number DFA
        lexeme, next_i = scan_number(source_code, i)
        if lexeme:
            st_index = st.insert(lexeme)
            pif.append(("number", st_index))
            i = next_i
            continue
        elif lexeme is None and char.isnumeric():
            malformed = source_code[i:next_i]
            errors.append(f"Lexical error: invalid number '{malformed}' at line {line_num}")
            i = next_i
            continue

        # 3. Check String DFA
        lexeme, next_i = scan_string(source_code, i)
        if lexeme:
            st_index = st.insert(lexeme)
            pif.append(("string", st_index))
            i = next_i
            continue

        # 4. Check Multi-character Operators
        if i + 1 < len(source_code):
            two_char = source_code[i:i + 2]
            if two_char in OPERATORS:
                pif.append((two_char, -1))
                i += 2
                continue

        # 5. Check Single-character Operators & Separators
        if char in OPERATORS or char in SEPARATORS:
            pif.append((char, -1))
            i += 1
            continue

        errors.append(f"Lexical error: unrecognized character '{char}' at line {line_num}")
        i += 1

    return pif, st, errors


if __name__ == "__main__":
    sample_program = Path(__file__).with_name("test.txt").read_text(encoding="utf-8")

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
