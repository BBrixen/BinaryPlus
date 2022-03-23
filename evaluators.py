# this is where i want to put all the int_eval, bool_eval, str_eval, and func_eval functions
# to hopefully decrease clutter in main.py
from errors import BinPValueError
from expressions import gen_bool_tree, eval_tree, gen_math_tree
from collections.abc import Callable

EVAL_FUNC = Callable[[int, str, list[int], dict], bool | str | int]


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


def str_eval(line_num: int, line: str, vals: list[str], local_namespace: dict) -> str:
    """
    This is where we calculate a string expression
    :param line: the entire line with the expression
    :param local_namespace: the namespace for checking any variables
    :return: the string result of calculating everything in vals
    """
    after_assignment = "".join(line.split('=')[1:])
    return namespace_replacement(line_num, after_assignment, local_namespace)[2:]  # 2: to remove spaces at start


def int_replacement(line_num: int, line: str, vals: list[str], local_namespace: dict) -> list[bool | str]:
    """
    This searches through a int expression and replaces any variable names with ints.
    :param line_num: the line of this expression for error message
    :param line: the entire line for error message
    :param vals: the vals to be converted into a list of bool vals
    :param local_namespace: the variables which could contain int values
    :return: a list of booleans and strings (the strings for any integer operators)
    """
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
        elif val in {"+", "-", "*", "/", "(", ")"}:
            retval.append(val)
        else:
            raise BinPValueError(line_num, line, message="Invalid cast of type 'int'")

    return retval


def int_eval(line_num: int, line: str, vals: list[str], local_namespace: dict) -> int:
    """
    This is where we compute an arithmetic expression for an integer
    :param line_num: the line number for error printing
    :param line: the entire line with the expression
    :param vals: a list of strings containing (hopefully) ints and +-*/%()
    :return: the integer result of calculating everything in vals
    """
    tokens = int_replacement(line_num, line, vals, local_namespace)
    root = gen_math_tree(tokens)
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
    match vals:
        case []:
            return []
        case [True | 'true' | 'True' | '1', *remaining]:
            return [True] + bool_replacement(line_num, line, remaining, local_namespace)
        case [False | 'false' | 'False' | '0', *remaining]:
            return [False] + bool_replacement(line_num, line, remaining, local_namespace)
        case ['&&' | '||' | '!', *remaining]:
            return [vals[0]] + bool_replacement(line_num, line, remaining, local_namespace)
        case [func_name, '(', *remaining]:
            index_of_end = remaining.index(')')
            function_call_name = func_name + '(' + " ".join(remaining[:index_of_end+1])
            function_return = determine_namespace_value(line_num, line, function_call_name, local_namespace)
            remaining = remaining[index_of_end+1:]
            return [function_return] + bool_replacement(line_num, line, remaining, local_namespace)
        case [variable, *remaining]:
            value = determine_namespace_value(line_num, line, variable, local_namespace)
            return [value] + bool_replacement(line_num, line, remaining, local_namespace)


def namespace_replacement(line_num: int, line: str, local_namespace: dict) -> str:
    # TODO: add support of tuple indexing in namespace search, this can be done in its own method
    """
    This nifty little function searches through a line and replaces every valid mention of a variable
    with its value inside the namespace
    :param line_num: the number of this line
    :param line: the raw line possibly containing variable names
    :param local_namespace: the namespace with variable names and values
    :return: the new line with variable names substituted with values
    """
    line = line.replace(' ( ', '(').replace(' ) ', ')')

    i = 0
    ignoring: bool = False  # used to ignore quoted sections
    while i < len(line):

        match line[i]:
            case ' ':  # don't count spaces
                i += 1
                continue
            case "'":  # this starts and ends quoted sections
                ignoring = not ignoring
        if ignoring:
            i += 1  # if it is quoted, then skip replacing it
            continue

        current_variable = find_variable_name(line, i)
        line = replace_variable(line_num, line, i, current_variable, local_namespace)
        i += 1

    return line


def find_variable_name(line: str, i: int) -> str:
    """
    We need to manually search for the next occurrence of a space, building a variable as we traverse
    :param line: the line to search
    :param i: current starting index which will construct a new variable
    :return: int with the new index after reaching a space, and a string with the variable name we found
    """
    current_variable: str = line[i]
    i += 1

    while i < len(line):  # manually split by spaces
        if line[i] == ' ':
            break
        current_variable += line[i]
        i += 1

    return current_variable


def replace_variable(line_num: int, line: str, i: int, variable_name: str, local_namespace: dict) -> str:
    """
    This replaces a possible variable name with its value in the namespace.
    it edits the line which contains the variable
    :param line_num: the number for this line of code
    :param line: the line which might contain the variable
    :param i: index of where the possible variable is located
    :param variable_name: string of either normal text or a variable which needs to be replaced
    :param local_namespace: namespace with variable names and values
    :return: the line with a variable replacement made if needed
    """

    val = str(determine_namespace_value(line_num, line, variable_name, local_namespace))
    line = line[:i] + val + line[i + len(val):]
    return line


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


def determine_namespace_value(line_num: int, line: str, variable_name: str, namespace: dict) -> str:
    """
    This will check if the variable exists in the namespace, either as a raw variable or as a function call
    :param" variable_name: the name of the variable
    :param namespace: namespace with all variable names
    :return: string representation of the variable value
    """
    from binp_functions import call_function
    if variable_name in namespace:
        return namespace[variable_name]

    if '(' in variable_name:
        split_func = variable_name.split('(')
        function_name = split_func[0]

        function_params = split_func[1][:-1]  # [-1] to remove the ) at the end
        function_params = [f.strip() for f in function_params.split(',')]

        while '' in function_params:
            function_params.remove('')

        val = call_function(line_num, line, function_name, function_params, namespace)
        return val

    return variable_name
