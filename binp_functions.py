from errors import BinPSyntaxError


class BinPFunction:
    def __init__(self, name: str, return_type: str, params: list[(str, str)], lines: list[str]):
        self._name = name
        self._return_type = return_type
        self._params = params
        self._lines = lines

    def run(self, params: list[str], function_namespace: dict):
        pass


def create_function(line_num: int, lines: list[str], return_type: str, name: str,
                    params: list[str]):
    print(f'creating a function with return type: {return_type} and name: {name}')
    print(f'it takes {params}')
    # parse params into (type, name)
    params = parse_parameter_declaration(line_num, lines[line_num], params)

    # find the lines of code that reference the function
    function_lines, end_line_num = parse_function_lines(line_num, lines, name)

    return BinPFunction(name, return_type, params, function_lines), end_line_num


def parse_parameter_declaration(line_num, line, params: list[str]) -> list[(str, str)]:
    if len(params) % 2 != 0:
        raise BinPSyntaxError(line_num, line, message="Incorrect Parameter Declaration")

    parsed_params = []
    for i in range(0, len(params), 2):
        type_name = (params[i], [params[i+1]])  # tuple of (type, name)
        parsed_params.append(type_name)

    return parsed_params


def parse_function_lines(line_num: int, lines: list[str], name: str) -> (list[str], int):
    end_line = line_num
    for i in range(line_num, len(lines)):
        line = lines[i].split()
        if line == ['end', name]:
            end_line = i
            break

    if end_line == line_num:
        raise BinPSyntaxError(line_num, lines[line_num], message=f"Unable to find end of func '{name}'")

    return lines[line_num:end_line], end_line


def call_function(line_num: int, line:str, name: str, params: list[str], larger_namespace: dict) -> None:
    pass

