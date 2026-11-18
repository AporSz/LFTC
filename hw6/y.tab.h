/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

#ifndef YY_YY_Y_TAB_H_INCLUDED
# define YY_YY_Y_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token kinds.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    YYEMPTY = -2,
    YYEOF = 0,                     /* "end of file"  */
    YYerror = 256,                 /* error  */
    YYUNDEF = 257,                 /* "invalid token"  */
    ID = 258,                      /* ID  */
    NUMBER = 259,                  /* NUMBER  */
    STRING = 260,                  /* STRING  */
    PLUS = 261,                    /* PLUS  */
    MINUS = 262,                   /* MINUS  */
    TIMES = 263,                   /* TIMES  */
    DIVIDE = 264,                  /* DIVIDE  */
    EQUALS = 265,                  /* EQUALS  */
    EQ = 266,                      /* EQ  */
    NE = 267,                      /* NE  */
    LT = 268,                      /* LT  */
    LE = 269,                      /* LE  */
    GT = 270,                      /* GT  */
    GE = 271,                      /* GE  */
    LPAREN = 272,                  /* LPAREN  */
    RPAREN = 273,                  /* RPAREN  */
    LBRACKET = 274,                /* LBRACKET  */
    RBRACKET = 275,                /* RBRACKET  */
    LBRACE = 276,                  /* LBRACE  */
    RBRACE = 277,                  /* RBRACE  */
    COMMA = 278,                   /* COMMA  */
    DOT = 279,                     /* DOT  */
    IMAGE = 280,                   /* IMAGE  */
    ARRAY = 281,                   /* ARRAY  */
    PIXEL = 282,                   /* PIXEL  */
    LOAD = 283,                    /* LOAD  */
    SAVE = 284,                    /* SAVE  */
    IF = 285,                      /* IF  */
    ELSE = 286,                    /* ELSE  */
    FOR = 287,                     /* FOR  */
    IN = 288,                      /* IN  */
    FUNCTION = 289,                /* FUNCTION  */
    RETURN = 290,                  /* RETURN  */
    VOID = 291,                    /* VOID  */
    SIZE = 292,                    /* SIZE  */
    AND = 293,                     /* AND  */
    OR = 294                       /* OR  */
  };
  typedef enum yytokentype yytoken_kind_t;
#endif
/* Token kinds.  */
#define YYEMPTY -2
#define YYEOF 0
#define YYerror 256
#define YYUNDEF 257
#define ID 258
#define NUMBER 259
#define STRING 260
#define PLUS 261
#define MINUS 262
#define TIMES 263
#define DIVIDE 264
#define EQUALS 265
#define EQ 266
#define NE 267
#define LT 268
#define LE 269
#define GT 270
#define GE 271
#define LPAREN 272
#define RPAREN 273
#define LBRACKET 274
#define RBRACKET 275
#define LBRACE 276
#define RBRACE 277
#define COMMA 278
#define DOT 279
#define IMAGE 280
#define ARRAY 281
#define PIXEL 282
#define LOAD 283
#define SAVE 284
#define IF 285
#define ELSE 286
#define FOR 287
#define IN 288
#define FUNCTION 289
#define RETURN 290
#define VOID 291
#define SIZE 292
#define AND 293
#define OR 294

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef int YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;


int yyparse (void);


#endif /* !YY_YY_Y_TAB_H_INCLUDED  */
