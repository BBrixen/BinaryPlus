from errors import BinPSyntaxError
from evaluators import bool_eval


def handle_if(line_num: int, lines: list[str], conditions: list[str], namespace: dict,
              execute=True, interactive=False, skip_input=False) -> (dict, int, list[str]):
    """
    This is called when the user calls an if statement. The format is one of the following
    if ([condition]) then
    [...]
    end

    if ([condition]) then
    [...]
    else
    [...]
    end
    This will run which ever function is valid for the given condition
    :param line_num: the line number of this if statement, for error printing
    :param lines: the lines of the program, used for traversing the if statement
    :param conditions: the list of all commands for this if, including the condition and the functions
    :param namespace: the namespace containing the functions which should be called
    :param execute: if this is false, we do not actually execute anything
    :param interactive: if this is false, we want to call a different run_condition that
                        instead allows the user to type lines one at a time
    :param skip_input: if this is true, we do not want to take input from the user
            during interactive mode (this is for while loop)
    :return: the modified namespace after the proper function has been called
    """
    bool_condition = False
    if execute:
        bool_condition = bool_eval(line_num, lines[line_num], conditions, namespace)

    if interactive:
        return run_condition_interactive(line_num + 1, lines, bool_condition, namespace,
                                         execute=execute, skip_input=skip_input)
    return run_condition(line_num + 1, lines, bool_condition, namespace, execute=execute)


def handle_while(line_num: int, lines: list[str], conditions: list[str], namespace: dict,
                 execute=True, interactive=False, skip_input=False) -> (dict, int, list[str]):
    """
    This creates a while loop. it is essentially the same as an if statement,
    except instead of going to the end of the if statement,
    it will instead tell the program to go back to the beginning of the while loop
    and start again. if the condition is false it will skip the entire while loop

    You can also provide an else statement which will execute once when the condition is false

    while ([condition]) then
    [...]
    end

    while ([condition]) then
    [...]
    else
    [...]
    end

    :param line_num: the line number for the start of the while loop
    :param lines: this is needed to parse through what is in the while loop
    :param conditions: the condition for the while loop to run
    :param namespace: the namespace which will be edited in this while loop
    :param execute: if this is false, do not actually execute anything inside the while loop
    :param interactive: if this is false, we want to call a different run_condition that
                        instead allows the user to type lines one at a time
    :param skip_input: if this is true, we do not want to take input from the user
            during interactive mode (this is for while loop)
    :return: this returns the modified namespace, along with the line number to go to next after this finishes
            it can also pass return values out of a function
    """
    line_of_while = line_num - 1  # -1 because we will add one after this is called. but we want to stay on this loop
    bool_condition = False
    if execute:
        bool_condition = bool_eval(line_num, lines[line_num], conditions, namespace)

    if interactive:
        namespace, line_num, retval = run_condition_interactive(line_num + 1, lines, bool_condition, namespace,
                                                                execute=execute, skip_input=skip_input)
    else:
        namespace, line_num, retval = run_condition(line_num + 1, lines, bool_condition, namespace, execute=execute)

    if retval is not None or not bool_condition:
        return namespace, line_num, retval  # set this to the end of the loop

    return namespace, line_of_while, retval


def run_condition(line_num: int, lines: list[str], condition: bool, namespace: dict,
                  execute=True) -> (dict, int, list[str]):
    """
    This runs through a conditional (if or while) and executes the code if it can
    It handles the end of the conditional, as well as any else blocks within it
    :param line_num: the line number for the first line of code after if/while starts
    :param lines: the lines of the program to loop over
    :param condition: the condition as an evaluated boolean
    :param namespace: the namespace which is used when running lines of code
    :param execute: if this is false, pass its false values onto the parse_line
            so that nothing in this section gets executed.
            we do 'condition and execute' because if either one of them is false,
            the specific line of code being parsed should not be executed
    :return: the namespace after the lines have been run,
            as well as the line number of the end of this conditional,
            and a retval if something was returned from this conditional
    """
    from main import parse_line

    if_statement_line_num = line_num  # stored for error printing later
    while line_num < len(lines):
        if lines[line_num] == '':
            line_num += 1
            continue
        first_elem = lines[line_num].split()[0]

        match first_elem:  # check the start of the line for end/else
            case 'end':
                return namespace, line_num, None
            case 'else':
                # WARNING: if conditionals break, then remove the 'and execute'
                condition = not condition and execute  # toggle condition (still keep this false if execute is false)
                line_num += 1

            case _:
                namespace, line_num, retval = parse_line(line_num, lines, namespace,
                                                         execute=(condition and execute))
                if retval is not None:  # we got a return from a function, so we need to pass it on
                    return namespace, line_num, retval

    raise BinPSyntaxError(line_num, lines[if_statement_line_num], message="Missing 'end' of if statement")


def run_condition_interactive(line_num: int, lines: list[str], condition: bool, namespace: dict,
                              execute=True, skip_input=False) -> (dict, int, list[str]):
    """
    This runs through a conditional (if or while) and executes the code if it can
    It handles the end of the conditional, as well as any else blocks within it

    This is different from above however, because it reads one line at a time
    from the user to determine the lines in the conditional
    :param line_num: the line number for the first line of code after if/while starts
    :param lines: the lines of the program to loop over
    :param condition: the condition as an evaluated boolean
    :param namespace: the namespace which is used when running lines of code
    :param execute: if this is false, pass its false values onto the parse_line
            so that nothing in this section gets executed.
            we do 'condition and execute' because if either one of them is false,
            the specific line of code being parsed should not be executed
    :param skip_input: if this is true, we do not want to take input from the user
            during interactive mode (this is for while loop)
    :return: the namespace after the lines have been run,
            as well as the line number of the end of this conditional,
            and a retval if something was returned from this conditional
    """
    from main import parse_line, format_line, INTERACTIVE_PRINT_NESTED

    while True:
        if not skip_input:
            line = format_line(input(INTERACTIVE_PRINT_NESTED))
            lines.append(line)
        else:
            line = lines[line_num]
        if line == '':
            line_num += 1
            continue
        first_elem = line.split()[0]
        match first_elem:  # check the start of the line for end/else
            case 'end':
                return namespace, line_num, None
            case 'else':
                # WARNING: if conditionals break, then remove the 'and execute'
                condition = not condition and execute  # toggle condition (still keep this false if execute is false)
                line_num += 1

            case _:
                namespace, line_num, retval = parse_line(line_num, lines, namespace,
                                                         execute=(condition and execute),
                                                         interactive=True,
                                                         skip_input=skip_input)
                if retval is not None:  # we got a return from a function, so we need to pass it on
                    return namespace, line_num, retval
