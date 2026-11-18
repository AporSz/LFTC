%option noyywrap noinput nounput prefix="source_"

%{
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "y.tab.h"

int pif_mode;
int lexical_errors;
void pif_close(void);

static FILE *pif_file;
static char **symbol_table;
static size_t symbol_capacity;

static void free_fields(char **fields, int count)
{
    int i;
    for (i = 0; i < count; ++i) {
        free(fields[i]);
    }
}

static int parse_csv_line(const char *line, char **fields, int max_fields)
{
    const char *cursor = line;
    int count = 0;

    while (*cursor != '\0' && *cursor != '\n' && *cursor != '\r') {
        char *value;
        size_t used = 0;
        size_t capacity = strlen(cursor) + 1;
        int quoted = (*cursor == '"');

        if (count == max_fields) {
            free_fields(fields, count);
            return -1;
        }

        value = malloc(capacity);
        if (value == NULL) {
            free_fields(fields, count);
            return -1;
        }

        if (quoted) {
            int closed = 0;
            ++cursor;
            while (*cursor != '\0') {
                if (*cursor == '"' && cursor[1] == '"') {
                    value[used++] = '"';
                    cursor += 2;
                } else if (*cursor == '"') {
                    ++cursor;
                    closed = 1;
                    break;
                } else {
                    value[used++] = *cursor++;
                }
            }
            if (!closed || (*cursor != ',' && *cursor != '\0' &&
                            *cursor != '\n' && *cursor != '\r')) {
                free(value);
                free_fields(fields, count);
                return -1;
            }
        } else {
            while (*cursor != '\0' && *cursor != ',' &&
                   *cursor != '\n' && *cursor != '\r') {
                value[used++] = *cursor++;
            }
        }

        value[used] = '\0';
        fields[count++] = value;

        if (*cursor == ',') {
            ++cursor;
            if (*cursor == '\0' || *cursor == '\n' || *cursor == '\r') {
                if (count == max_fields) {
                    free_fields(fields, count);
                    return -1;
                }
                fields[count] = strdup("");
                if (fields[count] == NULL) {
                    free_fields(fields, count);
                    return -1;
                }
                ++count;
                break;
            }
        } else {
            break;
        }
    }

    return count;
}

static int parse_index(const char *text, long *index)
{
    char *end;
    long value;

    errno = 0;
    value = strtol(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') {
        return -1;
    }
    *index = value;
    return 0;
}

static int set_symbol(long index, const char *lexeme)
{
    size_t needed;

    if (index < 0 || (unsigned long) index > 1000000UL) {
        return -1;
    }
    needed = (size_t) index + 1;
    if (needed > symbol_capacity) {
        size_t new_capacity = symbol_capacity == 0 ? 16 : symbol_capacity;
        char **new_table;
        while (new_capacity < needed) {
            new_capacity *= 2;
        }
        new_table = calloc(new_capacity, sizeof(*new_table));
        if (new_table == NULL) {
            return -1;
        }
        if (symbol_table != NULL) {
            memcpy(new_table, symbol_table, symbol_capacity * sizeof(*new_table));
            free(symbol_table);
        }
        symbol_table = new_table;
        symbol_capacity = new_capacity;
    }
    if (symbol_table[index] != NULL) {
        return -1;
    }
    symbol_table[index] = strdup(lexeme);
    return symbol_table[index] == NULL ? -1 : 0;
}

static int token_from_category(const char *category)
{
    if (strcmp(category, "id") == 0) return ID;
    if (strcmp(category, "number") == 0) return NUMBER;
    if (strcmp(category, "string") == 0) return STRING;
    if (strcmp(category, "+") == 0) return PLUS;
    if (strcmp(category, "-") == 0) return MINUS;
    if (strcmp(category, "*") == 0) return TIMES;
    if (strcmp(category, "/") == 0) return DIVIDE;
    if (strcmp(category, "=") == 0) return EQUALS;
    if (strcmp(category, "==") == 0) return EQ;
    if (strcmp(category, "!=") == 0) return NE;
    if (strcmp(category, "<") == 0) return LT;
    if (strcmp(category, "<=") == 0) return LE;
    if (strcmp(category, ">") == 0) return GT;
    if (strcmp(category, ">=") == 0) return GE;
    if (strcmp(category, "(") == 0) return LPAREN;
    if (strcmp(category, ")") == 0) return RPAREN;
    if (strcmp(category, "[") == 0) return LBRACKET;
    if (strcmp(category, "]") == 0) return RBRACKET;
    if (strcmp(category, "{") == 0) return LBRACE;
    if (strcmp(category, "}") == 0) return RBRACE;
    if (strcmp(category, ",") == 0) return COMMA;
    if (strcmp(category, ".") == 0) return DOT;
    if (strcmp(category, "image") == 0) return IMAGE;
    if (strcmp(category, "array") == 0) return ARRAY;
    if (strcmp(category, "pixel") == 0) return PIXEL;
    if (strcmp(category, "load") == 0) return LOAD;
    if (strcmp(category, "save") == 0) return SAVE;
    if (strcmp(category, "if") == 0) return IF;
    if (strcmp(category, "else") == 0) return ELSE;
    if (strcmp(category, "for") == 0) return FOR;
    if (strcmp(category, "in") == 0) return IN;
    if (strcmp(category, "function") == 0) return FUNCTION;
    if (strcmp(category, "return") == 0) return RETURN;
    if (strcmp(category, "void") == 0) return VOID;
    if (strcmp(category, "size") == 0) return SIZE;
    if (strcmp(category, "and") == 0 || strcmp(category, "&&") == 0) return AND;
    if (strcmp(category, "or") == 0 || strcmp(category, "||") == 0) return OR;
    return -1;
}

int pif_open(const char *pif_path, const char *st_path)
{
    FILE *st_file = fopen(st_path, "r");
    char *line = NULL;
    size_t line_capacity = 0;
    ssize_t line_length;
    int result = -1;

    if (st_file == NULL) {
        perror(st_path);
        return -1;
    }
    line_length = getline(&line, &line_capacity, st_file);
    if (line_length < 0) {
        fprintf(stderr, "Symbol table is empty: %s\n", st_path);
        goto cleanup;
    }
    while ((line_length = getline(&line, &line_capacity, st_file)) >= 0) {
        char *fields[3] = {NULL, NULL, NULL};
        long index;
        int count = parse_csv_line(line, fields, 3);
        if (count != 2 || parse_index(fields[0], &index) != 0 ||
            set_symbol(index, fields[1]) != 0) {
            fprintf(stderr, "Invalid symbol-table row in %s\n", st_path);
            free_fields(fields, count > 0 ? count : 0);
            goto cleanup;
        }
        free_fields(fields, count);
    }
    if (ferror(st_file)) {
        perror(st_path);
        goto cleanup;
    }
    result = 0;

cleanup:
    free(line);
    fclose(st_file);
    if (result != 0) {
        pif_close();
        return -1;
    }

    pif_file = fopen(pif_path, "r");
    if (pif_file == NULL) {
        perror(pif_path);
        pif_close();
        return -1;
    }
    line = NULL;
    line_capacity = 0;
    if (getline(&line, &line_capacity, pif_file) < 0) {
        fprintf(stderr, "PIF is empty: %s\n", pif_path);
        free(line);
        pif_close();
        return -1;
    }
    free(line);
    return 0;
}

int pif_next_token(void)
{
    char *line = NULL;
    size_t line_capacity = 0;
    ssize_t line_length;
    int token = 0;

    if (pif_file == NULL) {
        return 0;
    }
    line_length = getline(&line, &line_capacity, pif_file);
    if (line_length < 0) {
        free(line);
        return 0;
    }

    {
        char *fields[4] = {NULL, NULL, NULL, NULL};
        long st_index;
        int category_token;
        int count = parse_csv_line(line, fields, 4);

        if (count != 3 || parse_index(fields[2], &st_index) != 0) {
            fprintf(stderr, "Invalid PIF row\n");
            ++lexical_errors;
            token = YYUNDEF;
        } else {
            category_token = token_from_category(fields[1]);
            if (category_token < 0) {
                fprintf(stderr, "Unknown PIF token category: %s\n", fields[1]);
                ++lexical_errors;
                token = YYUNDEF;
            } else if (category_token == ID || category_token == NUMBER ||
                       category_token == STRING) {
                if (st_index < 0 || (unsigned long) st_index >= symbol_capacity ||
                    symbol_table[st_index] == NULL) {
                    fprintf(stderr, "PIF token refers to missing ST index: %ld\n", st_index);
                    ++lexical_errors;
                    token = YYUNDEF;
                } else {
                    token = category_token;
                }
            } else if (st_index != -1) {
                fprintf(stderr, "PIF token %s must have ST index -1\n", fields[1]);
                ++lexical_errors;
                token = YYUNDEF;
            } else {
                token = category_token;
            }
        }
        free_fields(fields, count > 0 ? count : 0);
    }

    free(line);
    return token;
}

void pif_close(void)
{
    size_t i;
    if (pif_file != NULL) {
        fclose(pif_file);
        pif_file = NULL;
    }
    for (i = 0; i < symbol_capacity; ++i) {
        free(symbol_table[i]);
    }
    free(symbol_table);
    symbol_table = NULL;
    symbol_capacity = 0;
}

void source_set_input(FILE *input)
{
    source_in = input;
}

static int keyword_token(const char *word)
{
    if (strcmp(word, "image") == 0) return IMAGE;
    if (strcmp(word, "array") == 0) return ARRAY;
    if (strcmp(word, "pixel") == 0) return PIXEL;
    if (strcmp(word, "load") == 0) return LOAD;
    if (strcmp(word, "save") == 0) return SAVE;
    if (strcmp(word, "if") == 0) return IF;
    if (strcmp(word, "else") == 0) return ELSE;
    if (strcmp(word, "for") == 0) return FOR;
    if (strcmp(word, "in") == 0) return IN;
    if (strcmp(word, "function") == 0) return FUNCTION;
    if (strcmp(word, "return") == 0) return RETURN;
    if (strcmp(word, "void") == 0) return VOID;
    if (strcmp(word, "size") == 0) return SIZE;
    if (strcmp(word, "and") == 0) return AND;
    if (strcmp(word, "or") == 0) return OR;
    return ID;
}
%}

%%

"=="                    return EQ;
"!="                    return NE;
"<="                    return LE;
">="                    return GE;
"&&"                    return AND;
"||"                    return OR;
"+"                     return PLUS;
"-"                     return MINUS;
"*"                     return TIMES;
"/"                     return DIVIDE;
"="                     return EQUALS;
"<"                     return LT;
">"                     return GT;
"("                     return LPAREN;
")"                     return RPAREN;
"["                     return LBRACKET;
"]"                     return RBRACKET;
"{"                     return LBRACE;
"}"                     return RBRACE;
","                     return COMMA;
"."                     return DOT;
0|[1-9][0-9]*           return NUMBER;
\"[^\"\n]*\"            return STRING;
[a-zA-Z][a-zA-Z0-9]*    return keyword_token(yytext);
[ \t\r\n]+              ;
.                       {
                            fprintf(stderr, "Lexical error: illegal character '%s'\n", yytext);
                            ++lexical_errors;
                        }

%%

int yylex_dispatch(void)
{
    return pif_mode ? pif_next_token() : source_lex();
}
