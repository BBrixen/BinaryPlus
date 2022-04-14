import sys


def eprint(*args, **kwargs):
    """
    A print() function which outputs to STDERR
    as opposed to STDOUT
    """
    print(*args, file=sys.stderr, **kwargs)


class BinPRuntimeError(SyntaxError):
    def __init__(self, line_num: int, line: str, message=''):
        self._num = line_num
        self._line = line
        self._message = f"Runtime Error on line {line_num+1}: {message}" \
                        f"\n{line}"
        super().__init__(self._message)


class BinPSyntaxError(SyntaxError):
    def __init__(self, line_num: int, line: str, message=''):
        self._num = line_num
        self._line = line
        self._message = f"Syntax Error on line {line_num+1}: {message}" \
                        f"\n{line}"
        super().__init__(self._message)


class BinPValueError(ValueError):
    def __init__(self, line_num: int, line: str, message=''):
        self._num = line_num
        self._line = line
        self._message = f"Value Error on line {line_num+1}: {message}" \
                        f"\n{line}"
        super().__init__(self._message)


class BinPArgumentError(ValueError):
    def __init__(self, line_num: int, line: str, message=''):
        self._num = line_num
        self._line = line
        self._message = f"Argument Error on line {line_num+1}: {message}" \
                        f"\n{line}"
        super().__init__(self._message)
