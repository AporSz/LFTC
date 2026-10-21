{%

#include <string.h>
#include <tables.h>

%}
operator            [+\-*/]
comparison_operator "=="|"!="|"<"|"<="|">"|">="
logical_operator    "and"|"or"|"&&"|"||"
number              0|[1-9][0-9]*
id                  [a-zA-Z][0-9a-zA-Z]*
string              \"[^\"\n]*\"
reserved_word       "image" | "array" | "pixel" | "load" | "save" | "if" | "else" | "for" | "in" | "function" | "return" | "void" | "size"
assign              "="
separator           [\(\)\[\],{}]

%%

{reserved_word}         {struct triple t; t.category = yytext; t.index = -1; t.token = "reserved word"; pif[pif_index++];}
{logical_operator}      {struct triple t; t.category = yytext; t.index = -1; t.token = "logical operator"; pif[pif_index++];}
{operator}              {struct triple t; t.category = yytext; t.index = -1; t.token = "operator"; pif[pif_index++];}
{comparison_operator}   {struct triple t; t.category = yytext; t.index = -1; t.token = "comparison operator"; pif[pif_index++];}
{assign}                {struct triple t; t.category = yytext; t.index = -1; t.token = "assignment operator"; pif[pif_index++];}
{number}                {struct triple t; t.category = "number constant"; int index = put(ht, yytext, "number"); t.index = index; t.token = strcat("number: ", yytext); pif[pif_index++];}
{string}                {struct triple t; t.category = "string constant"; int index = put(ht, yytext, "string"); t.index = index; t.token = strcat("string: ", yytext); pif[pif_index++];}
{id}                    {struct triple t; t.category = "id"; int index = put(ht, yytext, "id"); t.index = index; t.token = strcat("id: ", yytext); pif[pif_index++];}
{separator}             {struct triple t; t.category = yytext; t.index = -1; t.token = "separator"; pif[pif_index++];}
"{"[^}\n]*"}"           /* eat up one-line comments */
[ \t\n]+                /* eat up whitespace */
.                       printf( "Unrecognized character: %s\n", yytext );

%%

int main()
{
  ht = initHashTable(20);

  yylex();

  writeTables(ht, ):

  return 0;
}