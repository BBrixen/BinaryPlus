import sys

from errors import BinPSyntaxError, BinPValueError, BinPArgumentError
from evaluators import determine_evaluator


class BinPFunction:
    """
    This class represents a function which is callable

    they have the following syntax:
    var [type] func [name] = ([type name, type name...]) =>
    [...]
    end [name]

    example:
    var int func add1 = (int x) =>
        output 'x' before is x
        return x + 1
    end add1

    __init__: creates a function object which is a name, return type, parameters, and lines of program
    run: this is called to actually run the function
    __str__: is only used for debug purposes
    """
    def __init__(self, name: str, return_type: str, params: list[(str, str)], lines: list[str]):
        self._name = name
        self._return_type = return_type
        self._params = params
        self._lines = lines

    def __str__(self):
        """
        This is called when we output a function instead of its return type.
        This can be used for debugging function calls inside binp programs
        It has the following format:
        name: (param_type1, param_type2, ...) -> return_type
        :return: a string representation of this function
        """
        return f'{self._name}: ({", ".join(elem[0] for elem in self._params)}) -> {self._return_type}'

    def run(self, line_num: int, line: str, params: list, function_namespace: dict):
        """
        This runs the function by calling run_program on the lines of code for this function
        :param line_num: line number for errors
        :param line: line for errors
        :param params: the parameters passed into the function call
        :param function_namespace: the namespace which belongs to this function.
                we can change this as much as we want, it will not affect outer namespaces
        :return: a value which this function returns, possibly modifying the outer namespace
        """
        from main import run_program  # we put this inside the function to avoid an import loop

        # make sure the parameters passed are the correct length
        if len(params) != len(self._params) and (self._params == [] and params != [[]]):
            raise BinPArgumentError(line_num, line, message=f"Incorrect number of arguments in {self._name} call"
                                                            f"\nExpected: {self._params} \nGot: {params}")

        # modify the namespace with parameters passed in
        for i in range(len(self._params)):
            type_eval_func = determine_evaluator(self._params[i][0])
            params[i] = type_eval_func(line_num, line, params[i], function_namespace)
            function_namespace[self._params[i][1]] = params[i]

        end_line, function_return = run_program(self._lines, function_namespace)

        # returned nothing
        if function_return is None or function_return == [] or function_return == ['null']:
            if self._return_type != 'null':
                raise BinPValueError(line_num, line, message=f"Returned 'null' for type '{self._return_type}'")
            return 'null'

        return_eval = determine_evaluator(self._return_type)
        return return_eval(line_num, line, function_return, function_namespace)


def create_function(line_num: int, lines: list[str], return_type: str, name: str,
                    params: list[str], interactive=False):
    """
    This takes in a line and parses it into a BinPFunction object.
    We need to parse the parameters and determine which lines of the program are in this function
    :param line_num: the line number where the function starts
    :param lines: the entire lines of this block of code (either entire program or another function)
    :param return_type: the return type of this function
    :param name: the name of this function
    :param params: the parameters, which is an un-parsed list of alternating types and names
    :param interactive: if this is true, we are taking input from the user one line at a time
    :return: this returns a BinPFunction object as well as an integer for the line number of the end of the function
    """
    # parse params into (type, name)
    params = parse_parameter_declaration(line_num, lines[line_num], params)

    # find the lines of code that reference the function
    function_lines, end_line_num = parse_function_lines(line_num, lines, name, interactive=interactive)

    return BinPFunction(name, return_type, params, function_lines), end_line_num


def parse_parameter_declaration(line_num, line, params: list[str]) -> list[(str, str)]:
    """
    This takes an alternating list of types and names and converts it to a list of tuples of (type, name)
    :param line_num: the line number for error printing
    :param line: the line for error printing
    :param params: the parameters that need to be parsed
    :return: a list of (type, name) tuples for the parameters
    """
    param_len = len(params)
    if param_len % 3 != 2 and param_len != 0:
        raise BinPSyntaxError(line_num, line, message="Incorrect Parameter Declaration")

    parsed_params: list[(str, str)] = []
    i = 0
    while i <= param_len-2:
        type_name = (params[i], params[i+1])  # tuple of (type, name)
        parsed_params.append(type_name)

        if i+2 < param_len and params[i+2] != ',':
            raise BinPSyntaxError(line_num, line, message="Incorrect Parameter Declaration")
        i += 3

    return parsed_params


def parse_function_lines(line_num: int, lines: list[str], name: str, interactive=False) -> (list[str], int):
    """
    This determines which lines of the program are associated with a specific function. we are searching for:
    end [name]
    this marks the end of the function, in which case we return the correct lines
    as well as the line number for the end of this function
    :param line_num: the line number for the start of the number
    :param lines: the lines of the code which need to be associated with this function
    :param name: the name of this function
    :param interactive: if this is true, we are taking input from the user one line at a time
    :return: the lines for this function and the line number of the end
    """
    from main import format_line, INTERACTIVE_PRINT_NESTED
    if interactive:
        lines = []
        while True:
            try:
                line = format_line(input(INTERACTIVE_PRINT_NESTED))
                if line.split() == ['end', name]:
                    return lines, 0
                lines.append(line)
            except KeyboardInterrupt:
                sys.exit(3)

    end_line = line_num
    for i in range(line_num, len(lines)):
        line = lines[i].split()
        if line == ['end', name]:
            end_line = i
            break

    if end_line == line_num:
        raise BinPSyntaxError(line_num, lines[line_num], message=f"Unable to find end of func '{name}'")

    return lines[line_num+1:end_line], end_line


def call_function(line_num: int, line: str, name: str, params: list[str], namespace: dict) -> dict:
    """
    This serves as a middle ground between actually running the function.
    This needs to parse the information from running into usable information in the run function

    This may be called by namespace_replacement to substitute in the function value
    :param line_num: the number of this current line
    :param line: the line which calls the function
    :param name: the name of the function being called (to search for in namespace)
    :param params: the parameters passed into the function
    :param namespace: the larger_namespace which should not be modified by the function call
            (besides storing return values)
    :return: the value which the function returns
    """
    if name not in namespace:
        raise BinPValueError(line_num, line, message=f"Unable to find function '{name}'")

    for i in range(len(params)):  # this is needed we call a function on a line without any evaluation
        if params[i] in namespace:
            params[i] = namespace[params[i]]

    # formatting the parameters correctly (a list split by commas, each element is a list split by white space)
    params = " ".join([str(p) for p in params])
    params = [p.strip().split() for p in params.split(',')]

    func: BinPFunction = namespace[name]
    return func.run(line_num, line, params, namespace)


def parse_function_call(line_num: int, line: str, vals: list[str], namespace: dict,
                        index=0, depth=0) -> (list[str], int, dict):
    """
    This takes a list of values and recursively parses it into smaller
    function calls until we are at a base case.
    In that situation it calls the function and passes its return value
    to its caller. This means the value returns up the tree and continues
    to be used in further function calls.

    The end result is the list of values passed in, but every function
    call is replaced with its return value. This can then be stored as
    a parameter, or evaluated as a parameter in another function call
    (hence the recursive nature)
    :param line_num: the line number of the function parsing
    :param line: which line we are on for error printing
    :param vals: the values to parse for this current call
    :param namespace: used for running the function
    :param index: the index in this list to use. this is faster than popping, removing items, or slicing
    :param depth: the current function depth we are in,
            use this to evaluate parenthesis-wrapped expression inside functions
    :return: a list of values with function calls substituted in
            it also returns the index in the list where to continue parsing
    """
    new_namespace = namespace.copy()

    i = index
    parsed_vals = []
    while i < len(vals):
        try:
            if vals[i] in new_namespace and isinstance(namespace[vals[i]], BinPFunction) and vals[i+1] == '(':
                # if we have found a function name, and it has a parenthesis after it
                function_params, end_i, new_namespace = \
                    parse_function_call(line_num, line, vals, namespace, index=i+2, depth=0)

                # parsed the parameters recursively, now evaluate this function call
                function_return = call_function(line_num, line, vals[i], function_params, new_namespace)
                parsed_vals.append(function_return)
                i = end_i  # end_i is the index after we have evaluated this function,
                # that way we don't parse over already-parsed data

            elif vals[i] == '(':
                parsed_vals.append(vals[i])
                depth += 1  # increase depth counter by 1, so we don't exit from a function call too early
            elif vals[i] == ')':
                if depth > 0:
                    parsed_vals.append(vals[i])
                    depth -= 1  # closing out of a () expression
                else:
                    return parsed_vals, i, new_namespace  # closing out of a function

            else:
                parsed_vals.append(vals[i])
        except IndexError:
            raise BinPSyntaxError(line_num, line, message="Improper end to function call")

        i += 1

    return parsed_vals, len(vals), new_namespace
