# this is where i want to put all the int_eval, bool_eval, str_eval, and func_eval functions
# to hopefully decrease clutter in main.py
from errors import BinPValueError
from expressions import gen_bool_tree, eval_tree, gen_math_tree
from collections.abc import Callable

EVAL_FUNC = Callable[[int, str, list[int], dict], bool | str | int]
VALID_VARIABLE_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                            "abcdefghijklmnopqrstuvwxy1234567890_'"


def int_eval(line_num: int, line: str, vals: list[str], local_namespace: dict) -> int:
    """
    This is where we compute an arithmetic expression for an integer
    :param line_num: the line number for error printing
    :param line: the entire line with the expression
    :param vals: a list of strings containing (hopefully) ints and +-*/%()
    :param local_namespace: the namespace with all variables in it
    :return: the integer result of calculating everything in vals
    """
    tokens = int_replacement(line_num, line, vals, local_namespace)
    root = gen_math_tree(tokens)
    return eval_tree(root)


def int_replacement(line_num: int, line: str, vals: list[str], local_namespace: dict) -> list[bool | str]:
    """
    This searches through a int expression and replaces any variable names with ints.
    :param line_num: the line of this expression for error message
    :param line: the entire line for error message
    :param vals: the vals to be converted into a list of bool vals
    :param local_namespace: the variables which could contain int values
    :return: a list of booleans and strings (the strings for any integer operators)
    """
    vals = replace_all_variables(line_num, line, vals, local_namespace)
    retval = []

    for i, val in enumerate(vals):
        if val in local_namespace:
            if not isinstance(local_namespace[val], int):
                raise BinPValueError(line_num, line, message="Invalid cast of type 'int'")
            retval.append(local_namespace[val])
            continue

        if isinstance(val, int):
            retval.append(val)
        elif val.lstrip("-").isdecimal():
            retval.append(int(val))
        elif val in {"+", "-", "*", "/", "%", "(", ")"}:
            retval.append(val)
        else:
            raise BinPValueError(line_num, line, message="Invalid cast of type 'int'")

    return retval


def bool_eval(line_num: int, line: str, vals: list[str], local_namespace: dict) -> bool:
    """
    This is where we compute a boolean expression
    :param line_num: the line number for error printing
    :param line: the entire line with the expression
    :param vals: a list of strings containing (hopefully) bools along with or/and/()
    :param local_namespace: the namespace with possible boolean values to replace
    :return: the boolean result of calculating everything in vals
    """
    tokens = bool_replacement(line_num, line, vals, local_namespace)  # convert into all booleans or &&/||
    root = gen_bool_tree(tokens)
    return eval_tree(root)


def bool_replacement(line_num: int, line: str, vals: list[str], local_namespace: dict) -> list[bool | str]:
    """
    This searches through a boolean expression and replaces any variable names with booleans, and it also converts
    true/True/1 to True and false/False/0 to false

    This takes a recursive approach where we find the first value, add it to a list
    and then call it on the rest of the values, creating an entire list as we go
    :param line_num: the line of this expression for error message
    :param line: the entire line for error message
    :param vals: the vals to be converted into a list of bool vals
    :param local_namespace: the variables which could contain boolean values
    :return: a list of booleans and strings (the strings for any boolean operators)
    """
    vals = replace_all_variables(line_num, line, vals, local_namespace)
    vals = convert_str_to_ints(vals)
    retval = []

    for val in vals:
        match val:
            case True | 'true' | 'True':
                retval.append(True)
            case False | 'false' | 'False':
                retval.append(False)
            case '&&' | '||' | '(' | ')' | \
                 '==' | '!=' | '<' | '<=' | '>' | '>=' | \
                 int():
                retval.append(val)
            case _:
                raise BinPValueError(line_num, line, message="Invalid cast of type 'bool'")

    return retval


def str_eval(line_num: int, line: str, vals: list[str], local_namespace: dict) -> str:
    """
    This is where we calculate a string expression
    :param line_num: the current line in the program
    :param line: the entire line with the expression
    :param vals: the line split by spaces
    :param local_namespace: the namespace for checking any variables
    :return: the string result of calculating everything in vals
    """
    line = " " + line + " "
    start, end = 0, len(line)
    first_elem = vals[0]
    after_equals = False

    # these 2 while loops find the start and end line according to vals.
    # this allows us to remove unwanted string expression from the edges
    while start < len(line):
        if line[start] == '=':
            after_equals = True
        if after_equals and line[start - 1: start + len(first_elem) + 1] == f' {first_elem} ':
            break
        start += 1

    last_elem = vals[len(vals) - 1]
    while end > 0:
        if line[end - len(last_elem) - 1: end + 1] == f' {last_elem} ':
            break
        end -= 1
    line = line[1:]  # remove the spaces
    return namespace_replacement(line[start - 1:end], local_namespace)[:-2]


def namespace_replacement(line: str, local_namespace: dict) -> str:
    # TODO: add support of tuple indexing in namespace search, this can be done in its own method
    """
    This nifty little function searches through a line and replaces every valid mention of a variable
    with its value inside the namespace
    :param line: the raw line possibly containing variable names
    :param local_namespace: the namespace with variable names and values
    :return: the new line with variable names substituted with values
    """
    line = " " + line + " "
    for var in local_namespace:
        line = line.replace(f' {var} ', f' {local_namespace[var]} ')
    return line[1:]


def determine_evaluator(variable_type: str) -> EVAL_FUNC:
    """
    This takes in a type and returns the specific evaluator function for that type
    :param variable_type: the type of the variable(s)
    :return: the evaluator function for that type

    NOTE: ignore these type warnings, idk why pycharm is yelling at me, this is perfectly valid
    """
    match variable_type:
        case 'int':
            return int_eval
        case 'str':
            return str_eval
        case 'bool':
            return bool_eval
        case 'func':
            pass
        case 'null':
            pass
        case _:
            return str_eval


def replace_all_variables(line_num: int, line: str, vals: list[str], local_namespace: dict) -> list[str]:
    """
    This replaces every variable in the namespace with its value.
    it then looks for every function call and evaluates its return.
    at the end we have a list of values which can be parsed into
    a boolean or int tree

    :param line_num: the current line number for error printing
    :param line: the current line for error printing
    :param vals: the values that need to be replaced with variables or function returns
    :param local_namespace: the namespace with all variables and functions
    :return: list of all values replaced with their evaluation in the namespace
    """
    from binp_functions import BinPFunction, parse_function_call
    for i, val in enumerate(vals):
        if val in local_namespace and not isinstance(local_namespace[val], BinPFunction):
            vals[i] = local_namespace[val]

    vals, i, copied_namespace = parse_function_call(line_num, line, vals, local_namespace)
    return vals


def convert_str_to_ints(vals: list[str]) -> list[str, int]:
    """
    Given a list of strings, if a string holds an integer, it is converted to a
    Python integer object. If the string does not contain an integer,
    it is left alone and is not modified

    This function will not convert variables to numbers.
    If this is desired, @replace_all_variables should be called first.

    This function also assumes that each element does not have leading or trailing
    whitespace surrounding the elements

    :param vals: the values to search for strings containing integers
    :return a new list with int strings converted to integers
    """

    def convert_type(v):
        if type(v) == str and v.isdigit():
            return int(v)
        return v

    return list(map(convert_type, vals))
