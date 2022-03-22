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
    UNARY_NOT = object()
    OR = object()
    AND = object()
    GREATER_THAN = object()
    LESS_THAN = object()
    GREATER_EQUAL = object()
    LESS_EQUAL = object()
    EQUAL = object()
    NOT_EQUAL = object()

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

    def __str__(self):
        return self.name


BINARY_OPERATOR_MAP = {
    Operator.ADD: lambda x, y: x + y,
    Operator.SUB: lambda x, y: x - y,
    Operator.DIV: lambda x, y: x // y,
    Operator.MUL: lambda x, y: x * y,
    Operator.OR: lambda x, y: x or y,
    Operator.AND: lambda x, y: x and y,

    Operator.GREATER_THAN: lambda x, y: x > y,
    Operator.LESS_THAN: lambda x, y: x < y,
    Operator.GREATER_EQUAL: lambda x, y: x >= y,
    Operator.LESS_EQUAL: lambda x, y: x <= y,
    Operator.EQUAL: lambda x, y: x == y,
    Operator.NOT_EQUAL: lambda x, y: x != y
}


class OpNode:
    def __init__(self, op: Operator, val=None):
        self.op = op
        self.val = val
        self.left = None
        self.right = None


# TODO Remove namespace? (Not used at the moment)
def eval_tree(root: OpNode) -> int | bool:
    """
    Given a boolean tree or int tree, evaluate it into a single return value
    Function calls and variables are not supported; each node must either contain
    an operation or a constant value (10, false, etc.)

    This function assumes all the nodes are comparable
    (boolean operatores are not mixed with ints, etc.)

    :param root: The root of the expression tree
    :return: the evaluated boolean or integer from the given expression tree
    """
    match root.op:
        case Operator.INT | Operator.BOOL:
            return root.val

        case Operator.UNARY_NOT:
            return not root.val

        case x if x in BINARY_OPERATOR_MAP:
            binary_op_func = BINARY_OPERATOR_MAP[x]
            left = eval_tree(root.left)
            right = eval_tree(root.right)
            return binary_op_func(left, right)

        case _:
            assert False, "Invalid operator given"  # TODO Proper exception


def gen_math_tree(rhs: list[str]) -> OpNode:
    pass


def gen_bool_tree(tokens) -> OpNode | None:
    # TODO Account for parenthesis
    # TODO Reverse list and pop off last element for better performance
    print(tokens)
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
    # TODO Account for unary not
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
