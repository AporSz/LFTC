import argparse
import csv
from pathlib import Path

import ply.lex as lex
import ply.yacc as yacc

# --- 1. LEXER SPECIFICATION ---
tokens = [
    'ID', 'NUMBER', 'STRING', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'EQUALS', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE',
    'COMMA', 'DOT'
]

reserved = {
    'image': 'IMAGE',
    'array': 'ARRAY',
    'pixel': 'PIXEL',
    'load': 'LOAD',
    'save': 'SAVE',
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'in': 'IN',
    'function': 'FUNCTION',
    'return': 'RETURN',
    'void': 'VOID',
    'size': 'SIZE',
    'and': 'AND',
    'or': 'OR'
}

tokens = tokens + list(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='
t_EQ = r'=='
t_NE = r'!='
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_DOT = r'\.'
t_AND = r'&&'
t_OR = r'\|\|'


def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_NUMBER(t):
    r'0|[1-9][0-9]*'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'"[^"\n]*"'
    return t


t_ignore = ' \t\n'


def t_error(t):
    print(f"Lexical error: Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


lexer = lex.lex()


pif_token_types = {
    'id': 'ID',
    'number': 'NUMBER',
    'string': 'STRING',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'TIMES',
    '/': 'DIVIDE',
    '=': 'EQUALS',
    '==': 'EQ',
    '!=': 'NE',
    '<': 'LT',
    '<=': 'LE',
    '>': 'GT',
    '>=': 'GE',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    '{': 'LBRACE',
    '}': 'RBRACE',
    ',': 'COMMA',
    '.': 'DOT',
    '&&': 'AND',
    '||': 'OR',
    **reserved
}


class PIFLexer:
    def __init__(self, pif_path, st_path):
        self.symbols = {}
        with st_path.open(newline="", encoding="utf-8") as st_file:
            for row in csv.DictReader(st_file):
                index = int(row["ST Index"])
                if index in self.symbols:
                    raise ValueError(f"Duplicate symbol-table index {index}")
                self.symbols[index] = row["Lexeme"]

        with pif_path.open(newline="", encoding="utf-8") as pif_file:
            self.rows = list(csv.DictReader(pif_file))

        self.position = 0
        self.lineno = 1

    def token(self):
        if self.position >= len(self.rows):
            return None

        row = self.rows[self.position]
        self.position += 1
        category = row["Token/Category"]

        try:
            token_type = pif_token_types[category]
        except KeyError as error:
            raise ValueError(f"Unknown PIF token category {category!r}") from error

        symbol_index = int(row["ST Index"])
        if category in {"id", "number", "string"}:
            try:
                value = self.symbols[symbol_index]
            except KeyError as error:
                raise ValueError(
                    f"PIF token {category!r} refers to missing ST index {symbol_index}"
                ) from error
            if category == "number":
                value = int(value)
        else:
            if symbol_index != -1:
                raise ValueError(
                    f"PIF token {category!r} should not refer to an ST entry"
                )
            value = category

        token = lex.LexToken()
        token.type = token_type
        token.value = value
        token.lineno = self.lineno
        token.lexpos = self.position - 1
        return token


# --- 2. PARSER SPECIFICATION & PRODUCTION TRACKING ---
production_string = []

# defining epsilon
def p_empty(p):
    '''empty :'''
    p[0] = []

# <program>         ::= <statements>
def p_program(p):
    '''program : statements'''
    p[0] = p[1]
    production_string.append("program -> statements")

# <statements>      ::= <statement> <statements> | epsilon
def p_statement_list(p):
    '''statements : statement statements
                      | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
        production_string.append("statements -> statement statements")

    else:
        p[0] = []
        production_string.append("statements -> epsilon")

# <statement>       ::= <init> | <load> | <assign> | <save>
#                     | <if> | <for> | <function>
def p_statement(p):
    '''statement : init
                 | load
                 | assign
                 | save
                 | if_stmt
                 | for_stmt
                 | function'''
    p[0] = p[1]
    production_string.append(f"statement -> {p.slice[1].type}")

# <assign>          ::= <id> "=" <expression>
#                     | <id> "[" <index> "]" "=" <expression>
#                     | <id> "[" <index> "]" "[" <index> "]" "=" <expression>
def p_assign(p):
    '''assign : ID EQUALS expression
              | ID LBRACKET index RBRACKET EQUALS expression
              | ID LBRACKET index RBRACKET LBRACKET index RBRACKET EQUALS expression'''
    if len(p) == 4:
        p[0] = ('assign', p[1], p[3])
        production_string.append("assign -> ID = expression")
    elif len(p) == 7:
        p[0] = ('assign', p[1], p[3], p[6])
        production_string.append("assign -> ID [ index ] = expression")
    else:
        p[0] = ('assign', p[1], p[3], p[6], p[9])
        production_string.append("assign -> ID [ index ] [ index ] = expression")

# <save>            ::= "save" "(" <id> "," <string> ")"
def p_save(p):
    '''save : SAVE LPAREN ID COMMA STRING RPAREN'''
    p[0] = (p[3], p[5])
    production_string.append(f"save -> SAVE ( ID , STRING )")

# <load>            ::= "load" "(" <id> "," <string> ")"
def p_load(p):
    '''load : LOAD LPAREN ID COMMA STRING RPAREN'''
    p[0] = (p[3], p[5])
    production_string.append(f"load -> LOAD ( ID , STRING )")

#<init>            ::= "image" <id> "[" <index> "," <index> "]"
                    # | "array" <id> "[" <index> "]"
                    # | "pixel" <id> "[" <index> "," <index> "," <index> "," <index> "]"
                    # | "pixel" <id> "[" <index> "," <index> "," <index> "]"
def p_init(p):
    '''init : IMAGE ID LBRACKET index COMMA index RBRACKET
                | ARRAY ID LBRACKET index RBRACKET
                | PIXEL ID LBRACKET index COMMA index COMMA index RBRACKET
                | PIXEL ID LBRACKET index COMMA index COMMA index COMMA index RBRACKET'''
    if len(p) == 6:
        p[0] = ('init', p[2], p[4])
        production_string.append("init -> ARRAY ID [ index ]")
    elif len(p) == 8:
        p[0] = ('init', p[2], p[4], p[6])
        production_string.append("init -> IMAGE ID [ index , index ]")
    elif len(p) == 10:
        p[0] = ('init', p[2], p[4], p[6], p[8])
        production_string.append("init -> PIXEL ID [ index, index, index ]")
    else:
        p[0] = ('init', p[2], p[4], p[6], p[8], p[10])
        production_string.append("init -> PIXEL ID [ index, index, index, index ]")

# <if>              ::= "if" <logical_expression> "{" <statements> "}" "else" "{" <statements> "}"
                    # | "if" <logical_expression> "{" <statements> "}"
def p_if_stmt(p):
    '''if_stmt : IF logical_expression LBRACE statements RBRACE
               | IF logical_expression LBRACE statements RBRACE ELSE LBRACE statements RBRACE'''
    if len(p) == 6:
        p[0] = ('if', p[2], p[4])
        production_string.append("if -> IF logical_expression { statements }")
    else:
        p[0] = ('if', p[2], p[4], p[8])
        production_string.append("if -> IF logical_expression { statements } ELSE { statements }")

# <for>             ::= "for" <id> "in" <index> "{" <statements> "}"
def p_for_stmt(p):
    '''for_stmt : FOR ID IN index LBRACE statements RBRACE'''
    p[0] = ('for', p[2], p[4], p[6])
    production_string.append("for -> FOR ID IN index { statements }")

# <expression>        ::= <logical_expression>
def p_expression(p):
    '''expression : logical_expression'''
    p[0] = p[1]
    production_string.append("expression -> logical_expression")

# <logical_expression>            ::= <logical_expression_base> <logical_expression_tail>
def p_logical_expression(p):
    '''logical_expression : logical_expression_base logical_expression_tail'''
    p[0] = ('logical', p[1], p[2])
    production_string.append("logical_expression -> logical_expression_base logical_expression_tail")

# <logical_expression_base>       ::= <comparison_expression>
def p_logical_expression_base(p):
    '''logical_expression_base : comparison_expression'''
    p[0] = p[1]
    production_string.append("logical_expression_base -> comparison_expression")

# <logical_expression_tail>       ::= <logical_op> <logical_expression_base> <logical_expression_tail> | epsilon
def p_logical_expression_tail(p):
    '''logical_expression_tail : AND logical_expression_base logical_expression_tail
                               | OR logical_expression_base logical_expression_tail
                               | empty'''
    if len(p) == 4:
        p[0] = [(p[1], p[2])] + p[3]
        production_string.append(f"logical_expression_tail -> {p.slice[1].type} logical_expression_base logical_expression_tail")
    else:
        p[0] = []
        production_string.append("logical_expression_tail -> epsilon")

# <comparison_expression>         ::= <arithmetic_expression> <comp_op> <arithmetic_expression> | <arithmetic_expression>
def p_comparison_expression(p):
    '''comparison_expression : arithmetic_expression EQ arithmetic_expression
                             | arithmetic_expression NE arithmetic_expression
                             | arithmetic_expression LT arithmetic_expression
                             | arithmetic_expression LE arithmetic_expression
                             | arithmetic_expression GT arithmetic_expression
                             | arithmetic_expression GE arithmetic_expression
                             | arithmetic_expression'''
    if len(p) == 4:
        p[0] = ('comparison', p[1], p[2], p[3])
        production_string.append(f"comparison_expression -> arithmetic_expression {p[2]} arithmetic_expression")
    else:
        p[0] = p[1]
        production_string.append("comparison_expression -> arithmetic_expression")

# <arithmetic_expression>  ::= <arithmetic_expression> <additive_operator> <term>
#                            | <term>
def p_arithmetic_expression(p):
    '''arithmetic_expression : arithmetic_expression PLUS term
                             | arithmetic_expression MINUS term
                             | term'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
        production_string.append(f"arithmetic_expression -> arithmetic_expression {p[2]} term")
    else:
        p[0] = p[1]
        production_string.append("arithmetic_expression -> term")

# <term>                   ::= <term> <multiplicative_operator> <factor>
#                            | <factor>
def p_term(p):
    '''term : term TIMES factor
            | term DIVIDE factor
            | factor'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
        production_string.append(f"term -> term {p[2]} factor")
    else:
        p[0] = p[1]
        production_string.append("term -> factor")

# <factor>          ::= <id> | <number> | <function_call>
#                     | <id> "[" <index> "]"
#                     | <id> "[" <index> "]" "[" <index> "]"
#                     | "(" <arithmetic_expression> ")"
def p_factor(p):
    '''factor : ID
              | NUMBER
              | function_call
              | ID LBRACKET index RBRACKET
              | ID LBRACKET index RBRACKET LBRACKET index RBRACKET
              | LPAREN arithmetic_expression RPAREN'''
    if len(p) == 2:
        if p.slice[1].type == 'ID':
            p[0] = ('id', p[1])
            production_string.append("factor -> ID")
        elif p.slice[1].type == 'NUMBER':
            p[0] = ('number', p[1])
            production_string.append("factor -> NUMBER")
        else:
            p[0] = p[1]
            production_string.append("factor -> function_call")
    elif len(p) == 5:
        p[0] = ('index', p[1], p[3])
        production_string.append("factor -> ID [ index ]")
    elif len(p) == 8:
        p[0] = ('index', p[1], p[3], p[6])
        production_string.append("factor -> ID [ index ] [ index ]")
    else:
        p[0] = p[2]
        production_string.append("factor -> ( arithmetic_expression )")

# <index>           ::= <size> | <arithmetic_expression>
def p_index(p):
    '''index : size
             | arithmetic_expression'''
    p[0] = p[1]
    production_string.append(f"index -> {p.slice[1].type}")

# <size>            ::= <id> ".size"
def p_size(p):
    '''size : ID DOT SIZE'''
    p[0] = ('size', p[1])
    production_string.append("size -> ID . SIZE")

# <function_call>   ::= <identifier> "(" <arguments_opt> ")"
def p_function_call(p):
    '''function_call : ID LPAREN arguments_opt RPAREN'''
    p[0] = ('call', p[1], p[3])
    production_string.append("function_call -> ID ( arguments_opt )")

# <arguments_opt>   ::= <arguments> | epsilon
def p_arguments_opt(p):
    '''arguments_opt : arguments
                     | empty'''
    p[0] = p[1]
    production_string.append(f"arguments_opt -> {p.slice[1].type}")

# <arguments>       ::= <expression> <arguments_tail>
def p_arguments(p):
    '''arguments : expression arguments_tail'''
    p[0] = [p[1]] + p[2]
    production_string.append("arguments -> expression arguments_tail")

# <arguments_tail>  ::= "," <expression> <arguments_tail> | epsilon
def p_arguments_tail(p):
    '''arguments_tail : COMMA expression arguments_tail
                      | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
        production_string.append("arguments_tail -> , expression arguments_tail")
    else:
        p[0] = []
        production_string.append("arguments_tail -> epsilon")

# <function>        ::= "function" <identifier> "(" <parameter_opt> ")"
#                       "{" <statements> <return_opt> "}"
def p_function(p):
    '''function : FUNCTION ID LPAREN parameter_opt RPAREN LBRACE statements return_opt RBRACE'''
    p[0] = ('function', p[2], p[4], p[7], p[8])
    production_string.append("function -> FUNCTION ID ( parameter_opt ) { statements return_opt }")

# <return_opt>      ::= <return> | epsilon
def p_return_opt(p):
    '''return_opt : return_stmt
                  | empty'''
    p[0] = p[1]
    production_string.append(f"return_opt -> {p.slice[1].type}")

# <return>          ::= "return" <expression>
#                     | "return" "void"
def p_return_stmt(p):
    '''return_stmt : RETURN expression
                   | RETURN VOID'''
    if p.slice[2].type == 'VOID':
        p[0] = ('return', None)
        production_string.append("return -> RETURN VOID")
    else:
        p[0] = ('return', p[2])
        production_string.append("return -> RETURN expression")

# <parameters>      ::= <parameter> <parameter_tail>
def p_parameters(p):
    '''parameters : parameter parameter_tail'''
    p[0] = [p[1]] + p[2]
    production_string.append("parameters -> parameter parameter_tail")

# <parameter_tail>  ::= "," <parameter> <parameter_tail> | epsilon
def p_parameter_tail(p):
    '''parameter_tail : COMMA parameter parameter_tail
                      | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
        production_string.append("parameter_tail -> , parameter parameter_tail")
    else:
        p[0] = []
        production_string.append("parameter_tail -> epsilon")

# <parameter_opt>   ::= <parameters> | epsilon
def p_parameter_opt(p):
    '''parameter_opt : parameters
                     | empty'''
    p[0] = p[1]
    production_string.append(f"parameter_opt -> {p.slice[1].type}")

# <parameter>       ::= <identifier>
def p_parameter(p):
    '''parameter : ID'''
    p[0] = p[1]
    production_string.append("parameter -> ID")

def p_error(p):
    if p:
        print(f"Syntax error at token '{p.value}'")
    else:
        print("Syntax error at EOF")


parser = yacc.yacc(start='program', debug=False, write_tables=False)

# --- 3. TEST EXECUTION ---
if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="Parse DSL source.")
    argument_parser.add_argument(
        "--mode",
        choices=("pif", "source"),
        default="pif",
        help="read tokens from PIF.csv/ST.csv or tokenize source with PLY (default: pif)",
    )
    args = argument_parser.parse_args()

    production_string.clear()
    if args.mode == "pif":
        pif_path = Path(__file__).with_name("PIF.csv")
        st_path = Path(__file__).with_name("ST.csv")
        input_lexer = PIFLexer(pif_path, st_path)
        print("=== STARTING PARSING FROM PIF.csv AND ST.csv ===")
        result = parser.parse(lexer=input_lexer)
    else:
        source_path = Path(__file__).with_name("sample_code.txt")
        source_code = source_path.read_text(encoding="utf-8")
        print(f"=== STARTING PARSING FROM {source_path.name} WITH PLY LEX ===")
        result = parser.parse(source_code, lexer=lexer)

    print("\n=== STRING OF PRODUCTIONS (DERIVATION TRACE) ===")
    for idx, prod in enumerate(production_string, 1):
        print(f"{idx}. {prod}")

    if result is None:
        raise SystemExit("Parsing failed.")

    print("\nParsing completed successfully.")