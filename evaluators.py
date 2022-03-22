# this is where i want to put all the int_eval, bool_eval, str_eval, and func_eval functions
# to hopefully decrease clutter in main.py
from errors import BinPValueError
from expressions import gen_bool_tree, eval_tree


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
    root = gen_bool_tree(tokens, local_namespace)
    return eval_tree(root, local_namespace)


def bool_replacement(line_num: int, line: str, vals: list[str], local_namespace: dict) -> list[bool | str]:
    # TODO: need to accept ! for not
    """
    This searches through a boolean expression and replaces any variable names with booleans, and it also converts
    true/True/1 to True and false/False/0 to false
    :param line_num: the line of this expression for error message
    :param line: the entire line for error message
    :param vals: the vals to be converted into a list of bool vals
    :param local_namespace: the variables which could contain boolean values
    :return: a list of booleans and strings (the strings are && or ||)
    """
    retval = []
    for i, val in enumerate(vals):
        if val in local_namespace:
            if type(local_namespace[val]) is not bool:
                raise BinPValueError(line_num, line, message="Invalid cast of type 'bool'")
            retval.append(local_namespace[val])
            continue

        match val:
            case 'true' | 'True' | '1':
                retval.append(True)
            case 'false' | 'False' | '0':
                retval.append(False)
            case '&&' | '||':
                retval.append(val)
            case _:
                raise BinPValueError(line_num, line, message="Invalid cast of type 'bool'")

    return retval


def namespace_replacement(line: str, local_namespace: dict) -> str:
    # TODO: add support of tuple indexing in namespace search, this can be done in its own method
    """
    This nifty little function searches through a line and replaces every valid mention of a variable
    with its value inside the namespace
    :param line: the raw line possibly containing variable names
    :param local_namespace: the namespace with variable names and values
    :return: the new line with variable names substituted with values
    """

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
        line = replace_variable(line, i, current_variable, local_namespace)
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


def replace_variable(line: str, i: int, variable_name: str, local_namespace: dict) -> str:
    """
    This replaces a possible variable name with its value in the namespace.
    it edits the line which contains the variable
    :param line: the line which might contain the variable
    :param i: index of where the possible variable is located
    :param variable_name: string of either normal text or a variable which needs to be replaced
    :param local_namespace: namespace with variable names and values
    :return: the line with a variable replacement made if needed
    """
    if variable_name in local_namespace:
        val = str(local_namespace[variable_name])
        # comment the line below to remove "weird feature"
        # val = namespace_replacement(val, local_namespace)  # recursively call replacement to find nested variables
        line = line[:i] + val + line[i + len(variable_name):]
    return line


def str_eval(line: str, local_namespace: dict) -> str:
    """
    This is where we calculate a string expression
    :param line: the entire line with the expression
    :param local_namespace: the namespace for checking any variables
    :return: the string result of calculating everything in vals
    """
    after_assignment = "".join(line.split('=')[1:])
    return namespace_replacement(after_assignment, local_namespace)[2:]  # 2: to remove spaces at start


def int_eval(line_num: int, line: str, vals: list[str], local_namespace: dict) -> int:
    """
    This is where we compute an arithmetic expression for an integer
    :param line_num: the line number for error printing
    :param line: the entire line with the expression
    :param vals: a list of strings containing (hopefully) ints and +-*/%()
    :return: the integer result of calculating everything in vals
    """
    try:
        return int(vals[0])
    except ValueError:
        raise BinPValueError(line_num, line, message="Invalid cast of type 'int'")