grammar MyGrammar;

TYPE: 'char'|'integer'|'float'|'string';
fragment LETTER: [A-Za-z];
fragment DIGIT: [0-9];
fragment SIGN: [+|-];
fragment NONZERO_DIGIT: [1-9];
IDENTIFIER : '_' LETTER (LETTER|DIGIT)* ;
INTEGER : SIGN? NONZERO_DIGIT DIGIT* | '0' ;
FLOAT : INTEGER '.' DIGIT+ ;
SEPARATOR: '['|']'|'{'|'}'|'('|')';
ARITHMETICAL_OPERATOR: '='|'+'|'-'|'%'|'*'|'/';
RELATIONAL_OPERATOR: '=='|'!='|'<='|'<'|'>='|'>';

WS    : [ \t\r\n]+ -> skip ;

program: 'start' 'var' declist 'end-var' command_list 'end';

declist : declaration ';'
    | declaration ',' declist
    | declaration ';' declist;

declaration : TYPE IDENTIFIER;

command_list : command ';' | command ';' command_list;

command : simplecmd | structcmd;

simplecmd : assignment | iostmt | condition;

assignment : IDENTIFIER '=' expresion;

expresion : term
    | SEPARATOR term ARITHMETICAL_OPERATOR expresion SEPARATOR
    | expresion ARITHMETICAL_OPERATOR expresion;

term : IDENTIFIER | INTEGER | FLOAT;

iostmt : 'read' SEPARATOR IDENTIFIER SEPARATOR
    | 'write' SEPARATOR IDENTIFIER SEPARATOR;

structcmd: ifstmt | whilestmt | forstmt;

ifstmt : 'if' condition 'then' command_list 'end-if'
 | 'if' condition 'then' command_list 'else' command_list 'end-else' 'end-if';

condition : expresion RELATIONAL_OPERATOR expresion;

whilestmt : 'while' condition 'do' command_list 'end-while';

forstmt: 'for' IDENTIFIER ':' term 'then' command_list 'end-for';
