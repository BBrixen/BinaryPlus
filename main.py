#!/usr/bin/env python3.10

import re
import os
import sys

from errors import BinPSyntaxError, BinPValueError, BinPArgumentError, BinPRuntimeError, eprint
from functions import create_function, parse_function_call, BinPFunction
from evaluators import namespace_replacement, determine_evaluator
from conditionals import handle_if, handle_while

OPERANDS = "([!<>=]=|[<>=]|[\+-\/*,\.\$\(\)\%]|&&|\|\|)"
ADD_SPACES_INVERSE = re.compile(f" {OPERANDS} ")
ADD_SPACES = re.compile(OPERANDS)
INVALID_VARIABLE_NAMES = {'if', 'else', 'while', 'end', 'then', 'return', 'func', 'int', 'str', 'bool', 'fn', 'null',
                          'tup', 'var', 'output', 'input', 'true', 'false'}
VALID_VARIABLE_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789_')
BEGIN_PRINT = " >> "
INTERACTIVE_PRINT = " -- "
INTERACTIVE_PRINT_NESTED = ' ---- '
INTERACTIVE = False


def parse_line(line_num: int, lines: list[str], local_namespace: dict,
               execute=True, interactive=False, skip_input=False) -> (dict, int, list[str] | None):
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
    :param execute: if this is false, we do not want to execute this line of code,
            rather just act like we did, and move the line_number along accordingly
    :param interactive: if this is true, we are taking input from the user one line at a time
    :param skip_input: this is passed through to interactive while loops, so they don't ask
            for input after being created
    :return: the new namespace with added variables
    """
    retval = None

    match lines[line_num].split():
        case []:
            pass  # skip blank lines
        case ['$', *_]:
            pass  # skip comments

        case ['output', *_]:  # output a value
            if execute:
                output(lines[line_num][7:], local_namespace)

        case ['var', *x]:  # variable assignment
            if execute:
                local_namespace, line_num = var_assign(x, line_num, lines, local_namespace,
                                                       execute=execute, interactive=interactive)

        case ['if', '(', *conditions, ')', '=', '>']:  # if statement
            local_namespace, line_num, retval = handle_if(line_num, lines, conditions, local_namespace,
                                                          execute=execute,
                                                          interactive=interactive,
                                                          skip_input=skip_input)

        case ['while', '(', *conditions, ')', '=', '>']:  # while loop
            local_namespace, line_num, retval = handle_while(line_num, lines, conditions, local_namespace,
                                                             execute=execute,
                                                             interactive=interactive,
                                                             skip_input=skip_input)

        case [func_name, '(', *params, ')']:  # function call
            if execute:
                parse_function_call(line_num, lines[line_num], [func_name, '(', *params, ')'],
                                    local_namespace)

        case ['return', *vals]:  # returning a value
            if execute:
                return None, line_num, vals  # WARNING: might need to make this return local_namespace

        case _:
            raise BinPSyntaxError(line_num, lines[line_num])

    line_num += 1
    return local_namespace, line_num, retval  # return none when there are no return values to pass up


def var_assign(statements: list[str], line_num: int, lines: list[str], local_namespace: dict,
               execute=True, interactive=False) -> (dict, int):
    """
    This handles a variable assignment statement
    it has the form
    var type name = value(s)

    example:
    var int age = 42
    var str name = bennett
    var str description = name is age year(s) old
    :param statements: the list of statements comprising the variable assignment
            (without var because that has been removed)
    :param line_num: the line number for error messages
    :param lines: all the lines of this section of code
    :param local_namespace: the namespace which will be updates with the new variable
    :param execute: if this is false, we do not actually create the variable,
            but rather we act like we created it for keeping track of the line number
    :param interactive: if this is true, we are taking input from the user one line at a time
    :return: the new namespace with this variable added
    """
    line = lines[line_num]
    new_variable = None

    match statements:
        case [return_type, 'func', name, '=', '(', *params, ')', '=', '>']:  # function declaration
            # create function
            new_variable, line_num = \
                create_function(line_num, lines, return_type, name, params, interactive=interactive)

        case [var_type, name, '=', 'input']:
            if execute:
                raw_input = input(BEGIN_PRINT)  # use user input as the value
                raw_input = " ".join(re.split(ADD_SPACES, raw_input))

                eval_func = determine_evaluator(var_type)
                new_variable = eval_func(line_num, line[:-5] + raw_input, raw_input.split(), local_namespace)

        case [var_type, name, '=', *vals]:  # create type variable
            eval_func = determine_evaluator(var_type)
            new_variable = eval_func(line_num, line, vals, local_namespace)

        case _:
            raise BinPSyntaxError(line_num, line, message="Invalid variable assignment")

    if execute and new_variable is not None:
        name = valid_name(line_num, line, name)
        local_namespace[name] = new_variable
    return local_namespace, line_num


def valid_name(line_num, line, name: str) -> str:
    """
    This function checks that a variable name is valid
    :param line_num: the line number for error printing
    :param line: the line for error printing
    :param name: the name of the variable to check
    :return: the variable name if it is valid
    :throws: BinPSyntaxError if the name is invalid
    """
    if set(name).issubset(VALID_VARIABLE_CHARS) and \
            name not in INVALID_VARIABLE_NAMES and \
            not name[0].isdecimal():
        return name

    raise BinPSyntaxError(line_num, line, message="Invalid variable name. "
                                                  "Variables must start with alpha and cannot be a restricted term")


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
    line = "".join(re.split(ADD_SPACES_INVERSE, line))

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
        try:
            local_namespace, line_num, retval = parse_line(line_num, lines, local_namespace)
        except (BinPSyntaxError, BinPValueError, BinPArgumentError, BinPRuntimeError) as err:
            eprint(err)  # change this to 'raise err' if you want the stacktrace of the exception
            sys.exit(3)
        except (TypeError, AttributeError):
            err = BinPValueError(line_num, lines[line_num],
                                 message='Improper Type, most likely due to null type or improper variable assignment')
            eprint(err)
            sys.exit(3)
        except KeyboardInterrupt:
            sys.exit(3)
        except:  # we want to catch all other errors and apologize to the user
            err = BinPSyntaxError(line_num, lines[line_num],
                                  message='Oops, we appear to have an uncaught error. Sorry!')
            eprint(err)
            sys.exit(3)

        if retval is not None and retval != 'null':  # we got a return value from this function, so we need to pass on the return
            return lines[line_num], retval

    if not lines:
        return None, None
    return lines[line_num - 1], None  # return none since there was no return in this section


def run_interactive(local_namespace: dict) -> (str, None | list[str]):
    """
    We call this function when we want to run the interactive version of binary plus
    It takes singles lines from the user at a time and parses it.
    This allows the user to essentially type a program one line at a time and have it run as they type
    :param local_namespace: the namespace which holds all the variable definitions
    :return: returns
    """
    lines = []
    line_num = 0
    previous_line_num = -1
    print("Press Ctrl-C to exit the interactive prompt")
    while True:

        # get input (if we want to in this situation)
        new_line = None
        inputting = False
        try:
            if line_num != previous_line_num:
                new_line = format_line(input(INTERACTIVE_PRINT))
                lines.append(new_line)
                inputting = True
                line_num = len(lines) - 1
        except (KeyboardInterrupt, EOFError):
            sys.exit(3)

        try:
            previous_line_num = line_num
            local_namespace, line_num, retval = parse_line(line_num, lines, local_namespace, interactive=True,
                                                           skip_input=not inputting)

            if retval is not None:  # we got a return value from this function, so we need to pass on the return
                return lines[line_num], retval
        except (BinPSyntaxError, BinPValueError, BinPArgumentError) as err:
            eprint(err)
            line_num += 1


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
        line = format_line(line)
        retval.append(line)

    return retval


def format_line(line: str) -> str:
    """
    This takes a single line and formats it, so we can parse it properly
    We can use this in both format_file for running an entire program, or to format
    a single line for the interactive system
    :param line: a single line which will be run
    :return: the line formatted, so we can properly parse it
    """
    line = line.strip()  # remove extra whitespace and blank lines
    line = " ".join(re.split(ADD_SPACES, line))
    return line


def get_source_file():
    """
    Get the source filename from command line arguments via sys.argv
    (which is assumed to be the first argument passed into the function).
    It also assumes it has a filename to grab from the command line arguments
    (it will IndexError if sys.argv does not have index 1)
    **This exits the program via sys.exit() if the file does not exist**

    :returns the source file input from command line arguments
    """
    filename = sys.argv[1]
    if not os.path.exists(filename):
        eprint("The source program does not exist!")
        eprint(f"python {sys.argv[0]} <SOURCE PROGRAM> <ARGUMENTS>")
        sys.exit(1)

    if not os.path.isfile(filename):
        eprint("The input is not a file!")
        eprint(f"python {sys.argv[0]} <SOURCE PROGRAM> <ARGUMENTS>")
        sys.exit(1)

    if filename[-5:] != '.binp':
        eprint('Source file must be a .binp file!')
        eprint(f"python {sys.argv[0]} <SOURCE PROGRAM> <ARGUMENTS>")
        sys.exit(1)

    return filename


def get_cli_args(args) -> dict:
    """
    This takes the command line arguments passed to python and
    converts them to command line arguments in binp
    :param args: the arguments passed to this program
    :return: the global namespace with command line arguments
    """
    retval = {
        "ARG_COUNT": len(args)
    }
    for i in range(len(args)):
        retval[f"ARG_{i}"] = args[i]

    return retval


def get_unaries(global_namespace: dict) -> dict:
    """
    This defines two unary functions, int_negate and bool_negate,
    which are used to perform unary operations,
    since we do not have support for those in normal expressions
    :param global_namespace: the global namespace with command line arguments
    :return: the global namespace with two built-in functions added
    """
    int_negate_params = [('int', 'x')]
    int_negate_lines = [' return 0 - x ']
    int_negate = BinPFunction('int_negate', 'int', int_negate_params, int_negate_lines)
    global_namespace['int_negate'] = int_negate

    bool_negate_params = [('bool', 'x')]
    bool_negate_lines = [' if ( x ) = > ', ' return false ', ' end ', ' return true ']
    bool_negate = BinPFunction('bool_negate', 'bool', bool_negate_params, bool_negate_lines)
    global_namespace['bool_negate'] = bool_negate

    return global_namespace


def main() -> None:
    """
    takes a filename as an input, reads it and runs it as a binary+ program
    :return: the output for the program
    """
    args = sys.argv
    if len(args) <= 1:  # interactive version
        global_namespace = get_unaries({})  # interactive starts with no CLI and only unaries
        run_interactive(global_namespace)
        return

    # getting and loading file
    filename = get_source_file()
    try:
        file = open(filename)
    except OSError:
        eprint("Unable to open file")
        sys.exit(1)

    # running the code in the file
    global_namespace = {
        **get_cli_args(args[2:]),
    }
    global_namespace = get_unaries(global_namespace)
    lines = format_file(file)
    run_program(lines, global_namespace)


if __name__ == '__main__':
    main()
