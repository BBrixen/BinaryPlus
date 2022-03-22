from errors import BinPSyntaxError, BinPValueError

VALID_VARIABLE_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                            "abcdefghijklmnopqrstuvwxy1234567890_'"
ADD_SPACES = ['(', ')', '<', '>', '=', ' >  = ', ' <  = ']


def parse_line(line_num: int, line: str, local_namespace: dict) -> dict:
    """
    This is the highest level for parsing input. it handles:
        comments, output, variable assignment, if statements, while loops

    Each of these lines is passed into a new parser for that specific type
    It also throws CustomSyntaxErrors when parsing fails
    :param line_num: the current line number of the program
    :param line: the current like we are looking at
    :param local_namespace: namespace of the current line being run.
            this can be the global namespace or a copied namespace
            within a function call
    :return: the new namespace with added variables
    """
    match line.split():
        case []:
            pass  # skip blank lines
        case ['$', *_]:
            pass  # skip comments

        case ['output', *_]:
            output(line[7:], local_namespace)

        case ['var', *x]:
            local_namespace = var_assign(x, line_num, line, local_namespace)

        case default:
            raise BinPSyntaxError(line_num, default)
    return local_namespace


def var_assign(statements: list[str], line_num: int, line: str, local_namespace: dict) -> dict:
    """
    This handles a variable assignment statement
    it has the form
    var type name = value(s)

    :param statements: the list of statements comprising the variable assignment
            (without var because that has been removed)
    :param line_num: the line number for error messages
    :param line: the lines with the variable assignment
    :param local_namespace: the namespace which will be updates with the new variable
    :return: the new namespace with this variable added
    """
    match statements:
        case ['int', name, '=', *vals]:
            local_namespace[name] = int_eval(line_num, line, vals, local_namespace)
            return local_namespace

        case ['str', name, '=', *_]:
            local_namespace[name] = str_eval(line, local_namespace)
            return local_namespace

        case ['bool', name, '=', *vals]:
            local_namespace[name] = bool_eval(line_num, line, vals, local_namespace)
            return local_namespace

        case _:
            raise BinPSyntaxError(line_num, line, message="Invalid variable assignment")


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

        if val == 'true' or val == 'True' or val == '1':
            retval.append(True)
        elif val == 'false' or val == 'False' or val == '0':
            retval.append(False)
        elif val == '&&' or val == '||':
            retval.append(val)
        else:
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
    return str_namespace_replacement(after_assignment[1:], local_namespace)


def str_namespace_replacement(line: str, local_namespace: dict) -> str:
    # TODO: add support of tuple indexing in namespace search, this can be done in its own method
    """
    This nifty little function searches through a line and replaces every valid mention of a variable
    with its value inside the namespace
    :param line: the raw line possibly containing variable names
    :param local_namespace: the namespace with variable names and values
    :return: the new line with variable names substituted with values
    """

    for replacement in ADD_SPACES:
        line = line.replace(replacement, f' {replacement} ')

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

    for replacement in ADD_SPACES:
        line = line.replace(f' {replacement} ', replacement)

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
    if variable_name in local_namespace:
        val = str(local_namespace[variable_name])
        val = str_namespace_replacement(val, local_namespace)  # recursively call replacement to find nested variables
        # we have found a variable reference that is
        # not a part of another word/variable
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
    print(str_namespace_replacement(line, local_namespace))


def run_program(lines: list[str], local_namespace: dict) -> None:
    """
    This loops through the file and runs each line 1 by 1
    :param lines: the lines of this current program which need to be run
    :param local_namespace: the namespace for this current program run
            this could be global for the entire program or a copy for functions
    """
    for line_num, line in enumerate(lines):
        line = line.strip()  # remove extra whitespace and blank lines
        local_namespace = parse_line(line_num, line, local_namespace)


def main() -> None:
    """
    takes a filename as an input, reads it and runs it as a binary+ program
    :return: the output for the program
    """
    # filename = input()
    filename = 'test.binp'  # i have been using this for testing

    global_namespace = {}

    assert filename[-5:] == '.binp'

    try:
        file = open(filename)
        run_program(file.readlines(), global_namespace)
    except FileNotFoundError:
        assert False, "File does not exist"


if __name__ == '__main__':
    main()
