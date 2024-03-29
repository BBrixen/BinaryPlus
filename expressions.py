from enum import Enum

# An enumc class which holds valid types for each OpNode
class Operator(Enum):
    INT = object()
    BOOL = object()
    ADD = object()
    SUB = object()
    DIV = object()
    MUL = object()
    OR = object()
    AND = object()
    MODULUS = object()
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
    Operator.OR:  lambda x, y: x or y,
    Operator.AND: lambda x, y: x and y,

    Operator.MODULUS:       lambda x, y: x % y,
    Operator.GREATER_THAN:  lambda x, y: x > y,
    Operator.LESS_THAN:     lambda x, y: x < y,
    Operator.GREATER_EQUAL: lambda x, y: x >= y,
    Operator.LESS_EQUAL:    lambda x, y: x <= y,
    Operator.EQUAL:         lambda x, y: x == y,
    Operator.NOT_EQUAL:     lambda x, y: x != y
}

BOOL_OPERATORS = {
    "||": Operator.OR,
    "&&": Operator.AND,

    ">":  Operator.GREATER_THAN,
    "<":  Operator.LESS_THAN,
    ">=": Operator.GREATER_EQUAL,
    "<=": Operator.LESS_EQUAL,
    "==": Operator.EQUAL,
    "!=": Operator.NOT_EQUAL,
}


class OpNode:
    """
    This class is used to represent a series of operations
    in a tree-like manner. The root can contain either an operator
    or a value (a boolean or integer) and the leaves can be
    an OpNode subtree or None

    :param op: the operator which the node contains
    :param val: used if the node contains some sort of integer or boolean value
    """

    def __init__(self, op: Operator, val=None):
        self.op = op
        self.val = val
        self.left = None
        self.right = None

    def __repr__(self):
        return f"OpNode({repr(self.op)},{repr(self.val)})"


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

        case x if x in BINARY_OPERATOR_MAP:
            binary_op_func = BINARY_OPERATOR_MAP[x]
            left = eval_tree(root.left)
            right = eval_tree(root.right)
            return binary_op_func(left, right)

        case _:
            assert False, "Invalid operator given"


def gen_math_tree(tokens: list[str]) -> OpNode:
    """
    Given a list of tokens representing a mathematical expression,
    create a traversable tree that effectively represents evaluation heirarchy

    :param tokens: a list of tokens where each item (parens, plus, ints, etc.)
                   are separate elements within the list

    :returns: the root of the expression tree
    """
    return arith_expr(tokens)


def arith_expr(tokens: list[str]) -> OpNode:
    """
    The beginning of searching an arithmetic expression.

    :param tokens: a list of tokens which to parse into a tree
    :return: the root of the final parse tree
    """
    lchild = arith_term(tokens)
    return arith_expr1(tokens, lchild)


def arith_expr1(tokens: list[str], lchild: OpNode) -> OpNode:
    """
    Check if token list starts with a addition/subtraction operator.
    If so, handle the node creation now. Otherwise, return lchild

    :param tokens: a list of tokens which to parse into a tree
    :param lchild: the left child node to add to the mathmatical expression
    :return: the root of the parse tree
    """
    # Epsilon
    if len(tokens) == 0:
        return lchild

    match tokens[0]:
        case "+":
            op = Operator.ADD
        case "-":
            op = Operator.SUB
        case _:
            # Epsilon
            return lchild

    tokens.pop(0)
    root = OpNode(op)
    root.left = lchild
    root.right = arith_term(tokens)
    return arith_expr1(tokens, root)


def arith_term(tokens: list[str]) -> OpNode:
    """
    Check for higher precedence operators
    :param tokens: a list of tokens which to parse into a tree
    :return: the root of the parse tree
    """
    lchild = arith_factor(tokens)
    return arith_term1(tokens, lchild)


def arith_term1(tokens: list[str], lchild: OpNode) -> OpNode:
    """
    Check if token list starts with a multiplication/division/modulus operator.
    If so, handle the node creation now. Otherwise, return lchild

    :param tokens: a list of tokens which to parse into a tree
    :param lchild: the left child node to add to the mathmatical expression
    :return: the root of the parse tree
    """
    # Epsilon
    if len(tokens) == 0:
        return lchild

    match tokens[0]:
        case "*":
            op = Operator.MUL
        case "/":
            op = Operator.DIV
        case "%":
            op = Operator.MODULUS
        case _:
            # Epsilon
            return lchild

    tokens.pop(0)
    root = OpNode(op)
    root.left = lchild
    root.right = arith_factor(tokens)

    return arith_term1(tokens, root)


def arith_factor(tokens: list[str]) -> OpNode:
    """
    Check if the token list has an integer or paranthesis
    :param tokens: a list of tokens which to parse into a tree
    :return: the root of the parse tree
    """
    mine = tokens.pop(0)
    if isinstance(mine, int):
        return OpNode(Operator.INT, mine)

    assert mine == "(", "Invalid syntax. Expected parenthesis"
    root = arith_expr(tokens)
    assert tokens.pop(0) == ")", "Expected closing paranthesis"
    return root



def gen_bool_tree(tokens) -> OpNode | None:
    """
    Generate a simple boolean tree
    A tree can either have a single node (which is a value)
    or a tree can have a root node with two children

    :param tokens: a list of tokens which to parse into a tree
    :return: the root of the parse tree
    """
    if len(tokens) == 1:
        return bool_leaf(tokens[0])

    assert len(tokens) == 3, "A boolean expression must be two ints or booleans with a boolean operator in between"
    left, root, right = tokens
    root = bool_op(root)
    root.left = bool_leaf(left)
    root.right = bool_leaf(right)

    assert root.left.op == root.right.op, "Both operands must be of the same type"
    if root.left.op == Operator.BOOL:
        assert root.op in {Operator.AND, Operator.OR}, "Booleans only support && and || operations"
    return root


def bool_op(token: str) -> OpNode:
    """
    Pull a boolean operator from the beginning of the token stream
    :param tokens: a token to parse into a node
    :return: the root of the parse tree
    """
    assert token in BOOL_OPERATORS, "Operator is not a valid boolean operator"
    return OpNode(BOOL_OPERATORS[token])


def bool_leaf(token):
    """
    Pull an integer or boolean from the beginning of the token stream
    :param tokens: a token to parse into a node
    :return: the root of the parse tree
    """
    if type(token) == int:
        op = Operator.INT
    elif type(token) == bool:
        op = Operator.BOOL
    else:
        assert False, "Operand is not a boolean or integer"

    return OpNode(op, token)
