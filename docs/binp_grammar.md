TODO Finish (Part 1 in spec)

# Grammar Rules

Start rule: `prog`

```text
prog ::= <def_function> <prog>
      |  <var_decl> <prog>
      | -- epsilon --

var_type ::= bool | int | str | func

TODO Don't use regex
var_first_char ::= [a-zA-Z]+

TODO Don't use regex
var_other_char ::= [a-zA-Z0-9_]+

number ::= TODO
string ::= TODO
bool_expr ::= TODO
arith_expr ::= TODO

var_name ::= <var_first_char>
           | <var_first_char><var_other_char>

var_expr ::= <string> | <integer> | <bool_expr> | <arith_expr>

var_decl ::= var <var_type> <var_name> = <var_expr>

func_type ::= bool | int | str | null

param_list ::= TODO

TODO output declarations
code_stmt ::= <var_decl>
            | <func_decl>
            | <func_call>
            | <if_expr>
            | <while_expr>

code_stmts ::= <code_stmt> <code_stmts1>
code_stmts1 ::= <code_stmt> <code_stmts1>
            |  -- epsilon --

func_decl ::= var <func_type> func <var_name> = (<param_list>) =>
    <code_stmts>
end <var_name>

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

# left-factored and needs lchild
arith_expr1 -> + arith_term arith_expr1
             | - arith_term arith_expr1
             | -- epsilon --

arith_term -> arith_factor arith_term1

# left-factored and needs lchild
arith_term1 -> * arith_factor arith_term1
             | / arith_factor arith_term1
             | % arith_factor arith_term1
             | -- epsilon --

arith_factor -> ( arith_expr )
              | INTCON
```
