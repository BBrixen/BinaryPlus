from errors import BinPSyntaxError
from binp_functions import create_function, parse_function_call
from evaluators import namespace_replacement, determine_evaluator
from conditionals import handle_if, handle_while

ADD_SPACES = ['(', ')', '<', '>', '!', '&&', '||', '=', ',', '.', '-', '*', '+', '/', '$']
BEGIN_PRINT = " >> "


def parse_line(line_num: int, lines: list[str], local_namespace: dict) -> (dict, int, list[str] | None):
    """
    This is the highest level for parsing input. it handles:
        comments, output, variable assignment, if statements, while loops

    Each of these lines is passed into a new parser for that specific type
    It also throws CustomSyntaxErrors when parsing fails
    :param line_num: the current line number of the program
    :param lines: all the lines (needed to find end of functions)
    :param local_namespace: namespace of the current line being run.
            this can be the global namespace or a copied namespace
            within a function call
    :return: the new namespace with added variables
    """
    retval = None

    match lines[line_num].split():
        case []:
            pass  # skip blank lines
        case ['$', *_]:
            pass  # skip comments

        case ['output', *_]:  # output a value
            output(lines[line_num][7:], local_namespace)

        case ['var', *x]:  # variable assignment
            local_namespace, line_num = var_assign(x, line_num, lines, local_namespace)

        case['if', '(', *conditions, ')', 'then']:  # if statement
            local_namespace, line_num, retval = handle_if(line_num, lines, conditions, local_namespace)

        case ['while', '(', *conditions, ')', 'then']:  # while loop
            local_namespace, line_num, retval = handle_while(line_num, lines, conditions, local_namespace)

        case [func_name, '(', *params, ')']:  # function call
            parse_function_call(line_num, lines[line_num], [func_name, '(', *params, ')'], local_namespace)

        case ['return', *vals]:  # returning a value
            return None, line_num, vals  # TODO: might need to make this return local_namespace

        case default:
            raise BinPSyntaxError(line_num, default)

    line_num += 1
    return local_namespace, line_num, retval  # return none when there are no return values to pass up


def var_assign(statements: list[str], line_num: int, lines: list[str], local_namespace: dict) -> (dict, int):
    """
    This handles a variable assignment statement
    it has the form
    var type name = value(s)

    :param statements: the list of statements comprising the variable assignment
            (without var because that has been removed)
    :param line_num: the line number for error messages
    :param lines: all the lines of this section of code
    :param local_namespace: the namespace which will be updates with the new variable
    :return: the new namespace with this variable added
    """
    line = lines[line_num]

    match statements:
        case [return_type, 'func', name, '=', '(', *params, ')', '=', '>']:  # function declaration
            # create function
            local_namespace[name], line_num = create_function(line_num, lines, return_type, name, params)

        case [var_type, name, '=', 'input']:
            raw_input = input(BEGIN_PRINT)  # use user input as the value
            for replacement in ADD_SPACES:
                raw_input = raw_input.replace(replacement, f' {replacement} ')

            eval_func = determine_evaluator(var_type)
            local_namespace[name] = eval_func(line_num, line[:-5] + raw_input, raw_input.split(), local_namespace)

        case [var_type, name, '=', *vals]:  # create type variable
            eval_func = determine_evaluator(var_type)
            local_namespace[name] = eval_func(line_num, line, vals, local_namespace)

        case _:
            raise BinPSyntaxError(line_num, line, message="Invalid variable assignment")

    return local_namespace, line_num


def output(line: str, local_namespace: dict) -> None:
    """
    This searches through the output message and replaces any instances of a
    variable with its value.it does not replace variables surrounded with "" or ''
    :param line: the line to be searched. this can contain normal strings and
            variable references
    :param local_namespace: the namespace with every variable and its value
    :return: prints out the line to the console
    """

    line = namespace_replacement(line, local_namespace)
    for replacement in ADD_SPACES:
        line = line.replace(f' {replacement} ', replacement)

    line = line.replace("'", "")

    print(f'{BEGIN_PRINT}{line}')


def run_program(lines: list[str], local_namespace: dict) -> (str, None | list[str]):
    """
    This loops through the file and runs each line 1 by 1
    :param lines: the lines of this current program which need to be run
    :param local_namespace: the namespace for this current program run
            this could be global for the entire program or a copy for functions
    """
    line_num: int = 0
    while line_num < len(lines):
        local_namespace, line_num, retval = parse_line(line_num, lines, local_namespace)
        if retval is not None:  # we got a return value from this function, so we need to pass on the return
            return lines[line_num], retval

    if not lines:
        return [], None
    return lines[line_num-1], None  # return none since there was no return in this section


def format_file(file) -> list[str]:
    """
    This takes the file and converts it into a formatted list of lines
    We need to wrap certain characters in spaces so that they can be parsed easily with split()
    This adds spaces around each instance of those characters
    :param file: the file for the program
    :return: a list of lines of code in this file
    """
    lines = file.readlines()
    retval = []
    for line in lines:
        line = line.strip()  # remove extra whitespace and blank lines
        for replacement in ADD_SPACES:
            line = line.replace(replacement, f' {replacement} ')
        retval.append(line)

    return retval


def main() -> None:
    """
    takes a filename as an input, reads it and runs it as a binary+ program
    :return: the output for the program
    """
    # filename = input()
    filename = 'test.binp'  # I have been using this for testing

    global_namespace = {}
    assert filename[-5:] == '.binp'

    try:
        file = open(filename)
        lines = format_file(file)
        run_program(lines, global_namespace)
    except FileNotFoundError:
        assert False, "File does not exist"


if __name__ == '__main__':
    main()
