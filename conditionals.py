from errors import BinPSyntaxError
from evaluators import bool_eval


def handle_if(line_num: int, lines: list[str], conditions: list[str], namespace: dict,
              execute=True) -> (dict, int, list[str]):
    """
    This is called when the user calls an if statement. The format is one of the following
    if (condition) then if_function
    if (condition) then if_function else else_function
    This will run which ever function is valid for the given condition

    :param line_num: the line number of this if statement, for error printing
    :param lines: the lines of the program, used for traversing the if statement
    :param conditions: the list of all commands for this if, including the condition and the functions
    :param namespace: the namespace containing the functions which should be called
    :param execute: if this is false, we do not actually execute anything
    :return: the modified namespace after the proper function has been called
    """
    bool_condition = bool_eval(line_num, lines[line_num], conditions, namespace)
    namespace, new_num, retval = run_condition(line_num + 1, lines, bool_condition, namespace, execute=execute)
    return namespace, new_num, retval


def handle_while(line_num: int, lines: list[str], conditions: list[str], namespace: dict,
                 execute=True) -> (dict, int, list[str]):
    line_of_while = line_num - 1  # -1 because we will add one after this is called. but we want to stay on this loop
    bool_condition = bool_eval(line_num, lines[line_num], conditions, namespace)
    namespace, line_num, retval = run_condition(line_num + 1, lines, bool_condition, namespace, execute=execute)

    if retval is not None or not bool_condition:
        return namespace, line_num, retval  # set this to the end of the loop

    return namespace, line_of_while, retval


def run_condition(line_num: int, lines: list[str], condition: bool, namespace: dict,
                  execute=True) -> (dict, int, list[str]):
    from main import parse_line
    if_statement_line_num = line_num

    while line_num < len(lines):
        first_elem = lines[line_num].split()[0]

        match first_elem:
            case 'end':
                return namespace, line_num, None
            case 'else':
                condition = not condition
                line_num += 1
            case _:
                namespace, line_num, retval = parse_line(line_num, lines, namespace,
                                                         execute=(condition and execute))
                if retval is not None:  # we got a return from a function, so we need to pass it on
                    return namespace, line_num, retval

    raise BinPSyntaxError(line_num, lines[if_statement_line_num], message="Missing 'end' of if statement")
