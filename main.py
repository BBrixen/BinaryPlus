from errors import BinPSyntaxError, BinPValueError

VALID_VARIABLE_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                            "abcdefghijklmnopqrstuvwxy1234567890_'"


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
            output(line[6:], local_namespace)

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
    :return: the boolean result of calculating everything in vals
    """
    val = vals[0]
    if val == 'true' or val == 'True' or val == '1':
        return True
    elif val == 'false' or val == 'False' or val == '0':
        return False
    else:
        raise BinPValueError(line_num, line, message="Invalid cast of type 'bool'")


def str_eval(line: str, local_namespace: dict) -> str:
    """
    This is where we calculate a string expression
    :param line: the entire line with the expression
    :param local_namespace: the namespace for checking any variables
    :return: the string result of calculating everything in vals
    """
    after_assignment = "".join(line.split('=')[1:])
    return str_namespace_replacement(after_assignment, local_namespace)


def str_namespace_replacement(line: str, local_namespace: dict) -> str:
    """
    This nifty little function searches through a line and replaces every valid mention of a variable
    with its value inside the namespace
    :param line: the raw line possibly containing variable names
    :param local_namespace: the namespace with variable names and values
    :return: the new line with variable names substitued with values
    """
    line += ' '
    for variable in local_namespace:
        var_len = len(variable)

        for i in range(len(line) - var_len):
            substring = line[i:i + var_len]

            if substring == variable and line[i + var_len] not in VALID_VARIABLE_CHARACTERS \
                    and line[i - 1] not in VALID_VARIABLE_CHARACTERS:
                # we have found a variable reference that is
                # not a part of another word/variable
                line = line[:i] + str(local_namespace[variable]) + \
                       line[i + var_len:]

    return line[1:-1]


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
