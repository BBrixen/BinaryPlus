from errors import BinPSyntaxError, BinPValueError, BinPArgumentError
from evaluators import determine_evaluator


class BinPFunction:
    """
    This class represents a function which is callable

    __init__: creates a function object which is a name, return type, parameters, and lines of program
    run: this is called to actually run the function
    """
    def __init__(self, name: str, return_type: str, params: list[(str, str)], lines: list[str]):
        self._name = name
        self._return_type = return_type
        self._params = params
        self._lines = lines

    def __str__(self):
        return f'{self._name} takes {self._params} and returns {self._return_type}'

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
        if len(params) != len(self._params):
            raise BinPArgumentError(line_num, line, message=f"Incorrect number of arguments in {self._name} call")

        # modify the namespace with parameters passed in
        for i in range(len(self._params)):
            type_eval_func = determine_evaluator(self._params[i][0])
            params[i] = type_eval_func(line_num, line, [params[i]], function_namespace)
            function_namespace[self._params[i][1]] = params[i]

        end_line, function_return = run_program(self._lines, function_namespace)

        if function_return is None:
            if self._return_type != 'null':
                raise BinPValueError(line_num, line, message=f"Returned 'null' for type '{self._return_type}'")
            return 'null'

        return_eval = determine_evaluator(self._return_type)
        return_val = return_eval(line_num, line, function_return, function_namespace)
        return return_val


class FunctionTree:
    def __init__(self, binp_function: BinPFunction, vals: list[str]):
        self._function = binp_function
        self._vals_to_parse = vals

    def __repr__(self):
        return f'{self._function}' \
               f'we have these values: {self._vals_to_parse}'


def create_function(line_num: int, lines: list[str], return_type: str, name: str,
                    params: list[str]):
    """
    This takes in a line and parses it into a BinPFunction object.
    We need to parse the parameters and determine which lines of the program are in this function
    :param line_num: the line number where the function starts
    :param lines: the entire lines of this block of code (either entire program or another function)
    :param return_type: the return type of this function
    :param name: the name of this function
    :param params: the parameters, which is an un-parsed list of alternating types and names
    :return: this returns a BinPFunction object as well as an integer for the line number of the end of the function
    """
    # parse params into (type, name)
    params = parse_parameter_declaration(line_num, lines[line_num], params)

    # find the lines of code that reference the function
    function_lines, end_line_num = parse_function_lines(line_num, lines, name)

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


def parse_function_lines(line_num: int, lines: list[str], name: str) -> (list[str], int):
    """
    This determines which lines of the program are associated with a specific function. we are searching for:
    end [name]
    this marks the end of the function, in which case we return the correct lines
    as well as the line number for the end of this function
    :param line_num: the line number for the start of the number
    :param lines: the lines of the code which need to be associated with this function
    :param name: the name of this function
    :return: the lines for this function and the line number of the end
    """
    # TODO: need to change this from 'end name' to just 'end'
    end_line = line_num
    for i in range(line_num, len(lines)):
        line = lines[i].split()
        if line == ['end', name]:
            end_line = i
            break

    if end_line == line_num:
        raise BinPSyntaxError(line_num, lines[line_num], message=f"Unable to find end of func '{name}'")

    return lines[line_num+1:end_line], end_line


def call_function(line_num: int, line: str, name: str, params: list[str], larger_namespace: dict):
    """
    This serves as a middle ground between actually running the function.
    This needs to parse the information from running into usable information in the run function

    This may be called by namespace_replacement to substitute in the function value

    :param line_num: the line number for the function call
    :param line: the line which calls the function
    :param name: the name of the function being called (to search for in namespace)
    :param params: the parameters passed into the function
    :param larger_namespace: the larger_namespace which should not be modified by the function call
            (besides storing return values)
    :return: the value which the function returns
    """
    print(params)
    if name not in larger_namespace:
        raise BinPValueError(line_num, line, message=f"Unable to find function '{name}'")

    for i in range(len(params)):  # TODO: pretty sure i can remove this section
        if params[i] in larger_namespace:
            params[i] = larger_namespace[params[i]]

    func: BinPFunction = larger_namespace[name]
    return func.run(line_num, line, params, larger_namespace.copy())


def parse_function_call(line_num: int, line: str, vals: list[str], namespace: dict, index=0) -> (list[str], int):
    """
    Man this one is an interesting function

    :param line_num: the line number of the function parsing
    :param line: which line we are on for error printing
    :param vals: the values to parse for this current call
    :param namespace: used for running the function
    :return: a list of values with function calls substituted in
            it also returns the index in the list where to continue parsing
    """

    i = index
    parsed_vals = []
    while i < len(vals):
        try:
            if vals[i] in namespace and isinstance(namespace[vals[i]], BinPFunction) and vals[i+1] == '(':
                function_params, end_i = parse_function_call(line_num, line, vals, namespace, index=i+2)
                while ',' in function_params:
                    function_params.remove(',')

                function_return = call_function(line_num, line, vals[i], function_params, namespace)
                parsed_vals.append(function_return)
                i = end_i

            elif vals[i] == ')':
                return parsed_vals, i
            else:
                parsed_vals.append(vals[i])
        except IndexError:
            raise BinPSyntaxError(line_num, line, message="Improper end to function call")

        i += 1

    return parsed_vals, len(vals)
