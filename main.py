from errors import BinPSyntaxError, BinPValueError
from binp_functions import create_function, call_function
from expressions import gen_bool_tree, eval_tree

VALID_VARIABLE_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                            "abcdefghijklmnopqrstuvwxy1234567890_'"
ADD_SPACES = ['(', ')', '<', '>', '=', ' >  = ', ' <  = ']


def parse_line(line_num: int, lines: list[str], local_namespace: dict) -> (dict, int):
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
    match lines[line_num].split():
        case []:
            pass  # skip blank lines
        case ['$', *_]:
            pass  # skip comments

        case ['output', *_]:
            output(lines[line_num][7:], local_namespace)

        case ['var', *x]:
            local_namespace, line_num = var_assign(x, line_num, lines, local_namespace)

        case [func_name, '(', *params, ')']:
            call_function(line_num, lines[line_num], func_name, params, local_namespace)

        case default:
            raise BinPSyntaxError(line_num, default)

    new_line = line_num + 1  # by default, we only move 1 line at a time
    return local_namespace, new_line


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
        case [return_type, 'func', name, '=', '(', *params, ')', '=', '>']:
            # create function
            local_namespace[name], line_num = create_function(line_num, lines, return_type, name, params)

        case ['int', name, '=', *vals]:  # create int variable
            local_namespace[name] = int_eval(line_num, line, vals, local_namespace)

        case ['str', name, '=', *_]:  # create string variable
            local_namespace[name] = str_eval(line, local_namespace)

        case ['bool', name, '=', *vals]:  # create bool variable
            local_namespace[name] = bool_eval(line_num, line, vals, local_namespace)

        case _:
            raise BinPSyntaxError(line_num, line, message="Invalid variable assignment")

    return local_namespace, line_num


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


def str_eval(line: str, local_namespace: dict) -> str:
    """
    This is where we calculate a string expression
    :param line: the entire line with the expression
    :param local_namespace: the namespace for checking any variables
    :return: the string result of calculating everything in vals
    """
    after_assignment = "".join(line.split('=')[1:])
    return namespace_replacement(after_assignment, local_namespace)[2:]  # 2: to remove spaces at start



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

    print(line)


def run_program(lines: list[str], local_namespace: dict) -> None:
    """
    This loops through the file and runs each line 1 by 1
    :param lines: the lines of this current program which need to be run
    :param local_namespace: the namespace for this current program run
            this could be global for the entire program or a copy for functions
    """
    line_num: int = 0
    while line_num < len(lines):
        local_namespace, line_num = parse_line(line_num, lines, local_namespace)


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
    filename = 'expressions.binp'  # i have been using this for testing

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
