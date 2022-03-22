# TODO Support tuple addition and subtraction

from enum import Enum

# from errors import BinPSyntaxError


class Operator(Enum):
    INT = object()
    BOOL = object()
    ADD = object()
    SUB = object()
    DIV = object()
    MUL = object()
    # TODO Evaluate function and get return value (also make sure it returns an int)
    FUNC_CALL = object()
    VARIABLE = object()
    OR = object()
    AND = object()
    GREATER_THAN = object()
    LESS_THAN = object()
    GREATER_EQUAL = object()
    LESS_EQUAL = object()
    EQUAL = object()
    NOT_EQUAL = object()


BINARY_OPERATOR_MAP = {
    Operator.ADD: lambda x, y: x + y,
    Operator.SUB: lambda x, y: x - y,
    Operator.DIV: lambda x, y: x // y,
    Operator.MUL: lambda x, y: x * y,
    Operator.OR: lambda x, y: x or y,
    Operator.AND: lambda x, y: x and y,
    Operator.GREATER_THAN: lambda x, y: x > y,
    Operator.LESS_THAN: lambda x, y: x <= y,
    Operator.GREATER_EQUAL: lambda x, y: x >= y,
    Operator.LESS_EQUAL: lambda x, y: x <= y,
    Operator.EQUAL: lambda x, y: x == y,
    Operator.NOT_EQUAL: lambda x, y: x != y
}


class OpNode:
    def __init__(self, op: Operator, val=None):
        # Type hint is a string due to recursive definitions
        self.op = op
        self.val = val
        self.left = None
        self.right = None


def split_tokens(arr: list[str]):
    # Separate "(" and ")" into their own separate elements
    retval = []
    # TODO Also account for ! - boolean NOT
    for item in arr:
        if item.startswith("("):
            retval.append("(")
            retval.append(item.lstrip("("))
        # Not elif since an item can start with "(" and end with ")"
        if item.endswith(")"):
            retval.append(item.rstrip(")"))
            retval.append(")")

        if not item.startswith("(") and not item.endswith(")"):
            retval.append(item)
    return retval


def eval_tree(root: OpNode, namespace: dict[str]) -> int | bool:
    match root.op:
        # TODO Functions and variables
        case Operator.INT | Operator.BOOL:
            return root.val

        # TODO Handle function calls and variables

        case x:
            binary_op_func = BINARY_OPERATOR_MAP[x]
            left = eval_tree(root.left, namespace)
            right = eval_tree(root.right, namespace)
            return binary_op_func(left, right)


def gen_math_tree(rhs: list[str], namespace: dict) -> OpNode:
    pass


def gen_bool_tree(tokens, namespace) -> OpNode | None:
    # TODO Account for parenthesis
    root = bool_expr(tokens)
    return root


def bool_expr(tokens: list[str]):
    # TODO Account for parenthesis
    if len(tokens) == 0:
        return None

    mine = tokens.pop(0)
    assert isinstance(mine, bool), "Token is not a boolean"  # TODO Proper exception
    lchild = OpNode(Operator.BOOL, mine)
    return bool_op(tokens, lchild)


def bool_op(tokens: list[str], lchild: OpNode):
    if len(tokens) == 0:
        return lchild  # Epsilon

    mine = tokens.pop(0)
    if mine == "||":
        op = Operator.OR
    elif mine == "&&":
        op = Operator.AND
    # TODO NOT operator (need to ensure token list is set up correctly)
    else:
        assert False, "Incorrect boolean operator"  # TODO Proper exception

    root = OpNode(op)
    root.left = lchild
    root.right = bool_expr(tokens)

    return root
