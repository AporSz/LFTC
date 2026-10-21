%{

#include <string.h>
#include <tables.h>
#include <stdio.h>
#include <stdlib.h>

struct HashTable* ht;

%}

operator            [+\-*/]
comparison_operator "=="|"!="|"<"|"<="|">"|">="
logical_operator    "and"|"or"|"&&"|"||"
number              0|[1-9][0-9]*
id                  [a-zA-Z][0-9a-zA-Z]*
string              \"[^\"\n]*\"
reserved_word       ("image"|"array"|"pixel"|"load"|"save"|"if"|"else"|"for"|"in"|"function"|"return"|"void"|"size")
assign              "="
separator           [\(\)\[\],{}]
size                ".size"

%%

{reserved_word}         {struct triple t; t.category = "reserved word"; t.index = -1; t.token = concatStrings("", yytext); pif[pif_index++] = t;}
{logical_operator}      {struct triple t; t.category = "logical operator"; t.index = -1; t.token = concatStrings("", yytext); pif[pif_index++] = t;}
{operator}              {struct triple t; t.category = "operator"; t.index = -1; t.token = concatStrings("", yytext); pif[pif_index++] = t;}
{comparison_operator}   {struct triple t; t.category = "comparison operator"; t.index = -1; t.token = concatStrings("", yytext); pif[pif_index++] = t;}
{assign}                {struct triple t; t.category = "assignment operator"; t.index = -1; t.token = concatStrings("", yytext); pif[pif_index++] = t;}
{size}                  {struct triple t; t.category = "size"; t.index = -1; t.token = concatStrings("", yytext); pif[pif_index++] = t;}
{number}                {struct triple t; t.category = "number constant"; int index = put(ht, yytext, "number"); t.index = index; t.token = concatStrings("", yytext); pif[pif_index++] = t;}
{string}                {struct triple t; t.category = "string constant"; int index = put(ht, yytext, "string"); t.index = index; t.token = concatStrings("", yytext); pif[pif_index++] = t;}
{id}                    {struct triple t; t.category = "id"; int index = put(ht, yytext, "id"); t.index = index; t.token = concatStrings("", yytext); pif[pif_index++] = t;}
{separator}             {struct triple t; t.category = "separator"; t.index = -1; t.token = concatStrings("", yytext); pif[pif_index++] = t;}
[ \t\n]+                {}
.                       printf( "Unrecognized character: %s\n", yytext );

%%

int main(int argc, char* argv[])
{
  ht = initHashTable(100);

  FILE *fp = fopen(argv[1], "r");
  if(fp) yyin = fp;

  yylex();

  writeTables(ht, "output.txt");
  destroyHashTable(ht);
  for (int i=0; i<pif_index; i++) {
    free(pif[i].token);
  }

  return 0;
}