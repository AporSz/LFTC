%{
#include <stdio.h>
#include <string.h>

#define yylex yylex_dispatch
int yylex_dispatch(void);
extern FILE *source_in;
extern int pif_mode;
extern int lexical_errors;
int pif_open(const char *pif_path, const char *st_path);
int pif_next_token(void);
void pif_close(void);
void source_set_input(FILE *input);

static int syntax_errors;
static int production_number;

static void trace(const char *production)
{
    printf("%d. %s\n", ++production_number, production);
}

void yyerror(const char *message)
{
    fprintf(stderr, "Syntax error: %s\n", message);
    ++syntax_errors;
}
%}

%token ID NUMBER STRING
%token PLUS MINUS TIMES DIVIDE
%token EQUALS EQ NE LT LE GT GE
%token LPAREN RPAREN LBRACKET RBRACKET LBRACE RBRACE COMMA DOT
%token IMAGE ARRAY PIXEL LOAD SAVE IF ELSE FOR IN FUNCTION RETURN VOID SIZE
%token AND OR

%start program

%%

empty
    : /* empty */
    ;

program
    : statements
      { trace("program -> statements"); }
    ;

statements
    : statement statements
      { trace("statements -> statement statements"); }
    | empty
      { trace("statements -> epsilon"); }
    ;

statement
    : init
      { trace("statement -> init"); }
    | load
      { trace("statement -> load"); }
    | assign
      { trace("statement -> assign"); }
    | save
      { trace("statement -> save"); }
    | if_stmt
      { trace("statement -> if"); }
    | for_stmt
      { trace("statement -> for"); }
    | function
      { trace("statement -> function"); }
    ;

init
    : IMAGE ID LBRACKET index COMMA index RBRACKET
      { trace("init -> IMAGE ID [ index , index ]"); }
    | ARRAY ID LBRACKET index RBRACKET
      { trace("init -> ARRAY ID [ index ]"); }
    | PIXEL ID LBRACKET index COMMA index COMMA index RBRACKET
      { trace("init -> PIXEL ID [ index , index , index ]"); }
    | PIXEL ID LBRACKET index COMMA index COMMA index COMMA index RBRACKET
      { trace("init -> PIXEL ID [ index , index , index , index ]"); }
    ;

load
    : LOAD LPAREN ID COMMA STRING RPAREN
      { trace("load -> LOAD ( ID , STRING )"); }
    ;

save
    : SAVE LPAREN ID COMMA STRING RPAREN
      { trace("save -> SAVE ( ID , STRING )"); }
    ;

assign
    : ID EQUALS expression
      { trace("assign -> ID = expression"); }
    | ID LBRACKET index RBRACKET EQUALS expression
      { trace("assign -> ID [ index ] = expression"); }
    | ID LBRACKET index RBRACKET LBRACKET index RBRACKET EQUALS expression
      { trace("assign -> ID [ index ] [ index ] = expression"); }
    ;

if_stmt
    : IF logical_expression LBRACE statements RBRACE
      { trace("if -> IF logical_expression { statements }"); }
    | IF logical_expression LBRACE statements RBRACE ELSE LBRACE statements RBRACE
      { trace("if -> IF logical_expression { statements } ELSE { statements }"); }
    ;

for_stmt
    : FOR ID IN index LBRACE statements RBRACE
      { trace("for -> FOR ID IN index { statements }"); }
    ;

expression
    : logical_expression
      { trace("expression -> logical_expression"); }
    ;

logical_expression
    : logical_expression_base logical_expression_tail
      { trace("logical_expression -> logical_expression_base logical_expression_tail"); }
    ;

logical_expression_base
    : comparison_expression
      { trace("logical_expression_base -> comparison_expression"); }
    ;

logical_expression_tail
    : AND logical_expression_base logical_expression_tail
      { trace("logical_expression_tail -> AND logical_expression_base logical_expression_tail"); }
    | OR logical_expression_base logical_expression_tail
      { trace("logical_expression_tail -> OR logical_expression_base logical_expression_tail"); }
    | empty
      { trace("logical_expression_tail -> epsilon"); }
    ;

comparison_expression
    : arithmetic_expression EQ arithmetic_expression
      { trace("comparison_expression -> arithmetic_expression == arithmetic_expression"); }
    | arithmetic_expression NE arithmetic_expression
      { trace("comparison_expression -> arithmetic_expression != arithmetic_expression"); }
    | arithmetic_expression LT arithmetic_expression
      { trace("comparison_expression -> arithmetic_expression < arithmetic_expression"); }
    | arithmetic_expression LE arithmetic_expression
      { trace("comparison_expression -> arithmetic_expression <= arithmetic_expression"); }
    | arithmetic_expression GT arithmetic_expression
      { trace("comparison_expression -> arithmetic_expression > arithmetic_expression"); }
    | arithmetic_expression GE arithmetic_expression
      { trace("comparison_expression -> arithmetic_expression >= arithmetic_expression"); }
    | arithmetic_expression
      { trace("comparison_expression -> arithmetic_expression"); }
    ;

arithmetic_expression
    : arithmetic_expression PLUS term
      { trace("arithmetic_expression -> arithmetic_expression + term"); }
    | arithmetic_expression MINUS term
      { trace("arithmetic_expression -> arithmetic_expression - term"); }
    | term
      { trace("arithmetic_expression -> term"); }
    ;

term
    : term TIMES factor
      { trace("term -> term * factor"); }
    | term DIVIDE factor
      { trace("term -> term / factor"); }
    | factor
      { trace("term -> factor"); }
    ;

factor
    : ID
      { trace("factor -> ID"); }
    | NUMBER
      { trace("factor -> NUMBER"); }
    | function_call
      { trace("factor -> function_call"); }
    | ID LBRACKET index RBRACKET
      { trace("factor -> ID [ index ]"); }
    | ID LBRACKET index RBRACKET LBRACKET index RBRACKET
      { trace("factor -> ID [ index ] [ index ]"); }
    | LPAREN arithmetic_expression RPAREN
      { trace("factor -> ( arithmetic_expression )"); }
    ;

index
    : size
      { trace("index -> size"); }
    | arithmetic_expression
      { trace("index -> arithmetic_expression"); }
    ;

size
    : ID DOT SIZE
      { trace("size -> ID . SIZE"); }
    ;

function_call
    : ID LPAREN arguments_opt RPAREN
      { trace("function_call -> ID ( arguments_opt )"); }
    ;

arguments_opt
    : arguments
      { trace("arguments_opt -> arguments"); }
    | empty
      { trace("arguments_opt -> epsilon"); }
    ;

arguments
    : expression arguments_tail
      { trace("arguments -> expression arguments_tail"); }
    ;

arguments_tail
    : COMMA expression arguments_tail
      { trace("arguments_tail -> , expression arguments_tail"); }
    | empty
      { trace("arguments_tail -> epsilon"); }
    ;

function
    : FUNCTION ID LPAREN parameter_opt RPAREN LBRACE statements return_opt RBRACE
      { trace("function -> FUNCTION ID ( parameter_opt ) { statements return_opt }"); }
    ;

return_opt
    : return_stmt
      { trace("return_opt -> return"); }
    | empty
      { trace("return_opt -> epsilon"); }
    ;

return_stmt
    : RETURN expression
      { trace("return -> RETURN expression"); }
    | RETURN VOID
      { trace("return -> RETURN VOID"); }
    ;

parameter_opt
    : parameters
      { trace("parameter_opt -> parameters"); }
    | empty
      { trace("parameter_opt -> epsilon"); }
    ;

parameters
    : parameter parameter_tail
      { trace("parameters -> parameter parameter_tail"); }
    ;

parameter_tail
    : COMMA parameter parameter_tail
      { trace("parameter_tail -> , parameter parameter_tail"); }
    | empty
      { trace("parameter_tail -> epsilon"); }
    ;

parameter
    : ID
      { trace("parameter -> ID"); }
    ;

%%

int main(int argc, char **argv)
{
    int parse_result;

    if (argc == 4 && strcmp(argv[1], "--pif") == 0) {
        pif_mode = 1;
        if (pif_open(argv[2], argv[3]) != 0) {
            return 1;
        }
        printf("=== STARTING PARSING FROM PIF.csv AND ST.csv ===\n");
    } else if (argc == 3 && strcmp(argv[1], "--source") == 0) {
        FILE *source_file = fopen(argv[2], "r");
        if (source_file == NULL) {
            perror(argv[2]);
            return 1;
        }
        pif_mode = 0;
        source_set_input(source_file);
        printf("=== STARTING PARSING FROM SOURCE WITH FLEX ===\n");
    } else {
        fprintf(stderr, "Usage: %s --pif PIF.csv ST.csv | --source source.txt\n", argv[0]);
        return 2;
    }

    printf("\n=== STRING OF PRODUCTIONS (DERIVATION TRACE) ===\n");
    parse_result = yyparse();
    pif_close();

    if (source_in != NULL && source_in != stdin) {
        fclose(source_in);
        source_in = NULL;
    }

    if (parse_result != 0 || syntax_errors != 0 || lexical_errors != 0) {
        fprintf(stderr, "Parsing failed (%d syntax error(s), %d lexical error(s)).\n",
                syntax_errors, lexical_errors);
        return 1;
    }

    printf("\nParsing completed successfully.\n");
    return 0;
}
