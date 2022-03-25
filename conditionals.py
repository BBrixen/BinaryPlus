from errors import BinPSyntaxError
from evaluators import bool_eval


def handle_if(line_num: int, line: str, conditions: list[str], namespace: dict) -> dict:
    joined_condition = " ".join(conditions)
    split_by_then = joined_condition.split('then')
    if len(split_by_then) != 2:
        raise BinPSyntaxError(line_num, line, message="Must have exactly 1 'then' statement in a conditional")

    bool_condition = split_by_then[0].split()  # re split by spaces
    if bool_condition[0] != '(' or bool_condition[-1] != ')':
        raise BinPSyntaxError(line_num, line, message="Condition must be wrapped in parenthesis")

    bool_condition = bool_condition[1:-1]
    bool_condition = bool_eval(line_num, line, bool_condition, namespace)

    if bool_condition:
        pass
    else:
        pass

    return namespace
