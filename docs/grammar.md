# Grammar Rules

Start rule: `prog`

```text
prog ::= <def_function> <prog>
      |  <var_decl> <prog>
      |  <output_stmt>
      |  <comment>
      | -- epsilon --

letter ::= a | b | ... | z | A | B | ... | Z
number ::= 0 | 1 | ... | 9

var_type ::= bool | int | str | func

var_name ::= letter <var_name1>
var_name1 ::= letter <var_name1>
           | number <var_name1>
           | _ <var_name1>
           | -- epsilon --

var_expr ::= <string> | <integer> | <bool_expr> | <arith_expr>

integer ::= <number> <integer1>
integer1 ::= <number> <integer1>
          | -- epsilon --


var_decl ::= var <var_type> <var_name> = <var_expr>

func_type ::= bool | int | str | null

param_list ::= <var_type> <var_name>, <param_list>
            |  -- epsilon --

code_stmt ::= <var_decl>
            | <func_decl>
            | <func_call>
            | <if_expr>
            | <while_expr>
            | <output_stmt>

code_stmts ::= <code_stmt> <code_stmts1>
code_stmts1 ::= <code_stmt> <code_stmts1>
            |  -- epsilon --

func_decl ::= var <func_type> func <var_name> = (<param_list>) =>
    <code_stmts>
end <var_name>

comment ::= $ <rest_of_line>
output_stmt ::= output <rest_of_line>

func_call ::= <var_name>(<param_list>)

bool ::= true | True | false | False
bool_op ::= || | &&
num_op ::= == | != | < | <= | > | >=

bool_expr ::= <bool> <bool_op> <bool>
           |  <number> <num_op> <number>


if_expr ::= if (<bool_expr>) =>
                <code_stmts>
            end
          | if (<bool_expr>) =>
                <code_stmts>
            else =>
                <code_stmts>
            end


while_expr ::= while (<bool_expr>) =>
                <code_stmts>
            end
          | while (<bool_expr>) =>
                <code_stmts>
            else =>
                <code_stmts>
            end

arith_expr -> arith_term arith_expr1

arith_expr1 -> + arith_term arith_expr1
             | - arith_term arith_expr1
             | -- epsilon --

arith_term -> arith_factor arith_term1

arith_term1 -> * arith_factor arith_term1
             | / arith_factor arith_term1
             | % arith_factor arith_term1
             | -- epsilon --

arith_factor -> ( arith_expr )
              | INTCON
```
