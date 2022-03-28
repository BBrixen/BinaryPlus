from errors import BinPSyntaxError
from evaluators import bool_eval
from binp_functions import parse_function_call


def handle_if(line_num: int, line: str, conditions: list[str], namespace: dict) -> dict:
    """
    This is called when the user calls an if statement. The format is one of the following
    if (condition) then if_function
    if (condition) then if_function else else_function
    This will run which ever function is valid for the given condition

    :param line_num: the line number of this if statement, for error printing
    :param line: the line of this if statement, for error printing
    :param conditions: the list of all commands for this if, including the condition and the functions
    :param namespace: the namespace containing the functions which should be called
    :return: the modified namespace after the proper function has been called
    """
    # split it up into (condition) | functions
    joined_condition = " ".join(conditions)
    split_by_then = joined_condition.split(' then ')
    if len(split_by_then) != 2:
        raise BinPSyntaxError(line_num, line, message="Must have exactly 1 'then' statement in a conditional")

    bool_condition = split_by_then[0].split()  # split by spaces again, since we joined back together previously
    if bool_condition[0] != '(' or bool_condition[-1] != ')':
        raise BinPSyntaxError(line_num, line, message="Condition must be wrapped in parenthesis")

    # parse if there are a valid number of else statements
    functions = split_by_then[1].split(' else ')
    if len(functions) > 2:
        raise BinPSyntaxError(line_num, line, message="Must have 0-1 'else' statements in conditional")

    # evaluate the binary condition
    bool_condition = bool_condition[1:-1]
    bool_condition = bool_eval(line_num, line, bool_condition, namespace)

    if bool_condition:  # run if
        if_function = functions[0].split()
        temp_val, temp_i, namespace = parse_function_call(line_num, line, if_function, namespace)

    else:  # run else
        if len(functions) != 2:
            return namespace  # check if else exists or not
        else_function = functions[1].split()
        temp_val, temp_i, namespace = parse_function_call(line_num, line, else_function, namespace)

    return namespace
