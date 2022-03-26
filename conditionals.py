from errors import BinPSyntaxError
from evaluators import bool_eval
from binp_functions import parse_function_call


def handle_if(line_num: int, line: str, conditions: list[str], namespace: dict) -> dict:
    # split it up into (condition) | functions
    joined_condition = " ".join(conditions)
    split_by_then = joined_condition.split(' then ')
    if len(split_by_then) != 2:
        raise BinPSyntaxError(line_num, line, message="Must have exactly 1 'then' statement in a conditional")

    bool_condition = split_by_then[0].split()  # re split by spaces
    if bool_condition[0] != '(' or bool_condition[-1] != ')':
        raise BinPSyntaxError(line_num, line, message="Condition must be wrapped in parenthesis")

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
            return namespace
        else_function = functions[1].split()
        temp_val, temp_i, namespace = parse_function_call(line_num, line, else_function, namespace)

    return namespace
