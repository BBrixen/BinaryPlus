from enum import Enum
# from errors import BinPSyntaxError


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

BINARY_OPERATOR_STRING = {
    "+":  Operator.ADD,
    "-":  Operator.SUB,
    "/":  Operator.DIV,
    "*":  Operator.MUL,
    "||": Operator.OR,
    "&&": Operator.AND,

    "%":  Operator.MODULUS,
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
            assert False, "Invalid operator given"  # TODO Proper exception


def gen_math_tree(tokens: list[str]) -> OpNode:
    """
    Given a list of tokens representing a mathematical expression,
    create a traversable tree that effectively represents evaluation heirarchy

    :param tokens: a list of tokens where each item (parens, plus, ints, etc.)
                   are separate elements within the list

    :returns: the root of the expression tree
    """
    return arith_expr(tokens)


"""
Precedence (Lowest to Highest):
    +, -
    *, /, %
    parenthesis

arith_expr -> arith_term arith_expr1

# left-factored and needs lchild
arith_expr1 -> + arith_term arith_expr1
             | - arith_term arith_expr1
             | -- epsilon --

arith_term -> arith_factor arith_term1

# left-factored and needs lchild
arith_term1 -> * arith_factor arith_term1
             | / arith_factor arith_term1
             | % arith_factor arith_term1
             | -- epsilon --

arith_factor -> ( arith_expr )
              | INTCON

"""


# TODO Docstrings

def arith_expr(tokens: list[str]) -> OpNode:
    lchild = arith_term(tokens)
    return arith_expr1(tokens, lchild)


def arith_expr1(tokens: list[str], lchild: OpNode) -> OpNode:
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
    lchild = arith_factor(tokens)
    return arith_term1(tokens, lchild)


def arith_term1(tokens: list[str], lchild: OpNode) -> OpNode:
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
    mine = tokens.pop(0)
    if isinstance(mine, int):
        return OpNode(Operator.INT, mine)

    assert mine == "(", "Invalid syntax. Expected parenthesis"  # TODO Proper exception
    root = arith_expr(tokens)
    assert tokens.pop(0) == ")", "Expected closing paranthesis"  # TODO Proper exception
    return root


def gen_bool_tree(tokens) -> OpNode | None:
    # TODO Account for parenthesis and negation
    # TODO Reverse list and pop off last element for better performance
    #  maybe use an index parameter instead of popping elements
    #  (check parse_function_call in bin_p_functions.py for an example)
    # print(tokens)
    root = bool_expr(tokens)
    return root


def bool_expr(tokens: list[str]):
    if len(tokens) == 0:
        return None

    mine = tokens.pop(0)
    if isinstance(mine, bool):
        op = Operator.BOOL
    elif isinstance(mine, int):
        op = Operator.INT
    else:
        assert type(mine) in {int, bool}, "Token is not a boolean"  # TODO Proper exception

    lchild = OpNode(op, mine)
    return bool_op(tokens, lchild)


def bool_op(tokens: list[str], lchild: OpNode):
    if len(tokens) == 0:
        return lchild  # Epsilon

    mine = tokens.pop(0)
    if mine not in BINARY_OPERATOR_STRING:
        assert False, "Incorrect boolean operator"  # TODO Proper exception

    op = BINARY_OPERATOR_STRING[mine]

    root = OpNode(op)
    root.left = lchild
    root.right = bool_expr(tokens)

    return root


# TODO Remove
if __name__ == "__main__":
    tokens = [1, "!=", 1, "||", True]
    root = gen_bool_tree(tokens)
    print(eval_tree(root))
