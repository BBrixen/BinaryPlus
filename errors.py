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
