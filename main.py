from errors import CustomSyntaxError

VALID_VARIABLE_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                            "abcdefghijklmnopqrstuvwxy1234567890_'"


def parse_line(line_num: int, line: str, local_namespace: dict) -> bool:
    """
    This is the highest level for parsing input. it handles:
        comments, output, variable assignment, if statements, while loops

    Each of these lines is passed into a new parser for that specific type
    It also throws CustomSyntaxErrors when parsing fails
    :param line_num: the current line number of the program
    :param line: the current like we are looking at
    :param local_namespace: namespace of the current line being run.
            this can be the global namespace or a copied namespace within a function
    :return: true if this line is valid and ran
    :throws: CustomSyntaxError if the line is invalid
    """
    match line.split():
        case ['$', *x]:
            return False
        case ['output', *_]:
            output(line[6:], local_namespace)
        case default:
            raise CustomSyntaxError(line_num, default)


def output(line: str, local_namespace: dict) -> None:
    """
    This searches through the output message and replaces any instances of a
    variable with its value.it does not replace variables surrounded with "" or ''
    :param line: the line to be searched. this can contain normal strings and
            variable references
    :param local_namespace: the namespace with every variable and its value
    :return: prints out the line to the console
    """
    line += ' '
    for variable in local_namespace:
        var_len = len(variable)
        for i in range(len(line) - var_len):
            substring = line[i:i + var_len]
            if substring == variable and \
                    line[i+var_len] not in VALID_VARIABLE_CHARACTERS and \
                    line[i-1] not in VALID_VARIABLE_CHARACTERS:
                # we have found a variable reference that is
                # not a part of another word/variable
                line = line[:i] + str(local_namespace[variable]) + \
                       line[i + var_len:]
    print(line[1:])


def run_program(lines: list[str], local_namespace: dict) -> None:
    """
    This loops through the file and runs each line 1 by 1
    :param lines: the lines of this current program which need to be run
    :param local_namespace: the namespace for this current program run
            this could be global for the entire program or a copy for functions
    """
    for line_num, line in enumerate(lines):
        line = line.strip()  # remove extra whitespace and blank lines
        valid: bool = parse_line(line_num, line, local_namespace)
        if valid:
            pass  # where we will run this line of code


def main() -> None:
    """
    takes a filename as an input, reads it and runs it as a binary+ program
    :return: the output for the program
    """
    filename = input()
    # filename = 'test.binp'  # i have been using this for testing

    global_namespace = {}
    global_namespace['x'] = 10

    assert filename[-5:] == '.binp'

    try:
        file = open(filename)
        run_program(file.readlines(), global_namespace)
    except FileNotFoundError:
        assert False, "File does not exist"


if __name__ == '__main__':
    main()
