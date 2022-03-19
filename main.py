from errors import CustomSyntaxError


def parse_line(line_num: int, line: str, local_namespace: dict) -> bool:
    match line.split():
        case ['$', *x]:
            return False
        case ['output', *_]:
            output(line[6:], local_namespace)
        case default:
            raise CustomSyntaxError(line_num, default)


def output(line: str, local_namespace: dict) -> None:
    line += ' '
    for variable in local_namespace:
        line = line.replace(f' {variable} ', f' {local_namespace[variable]} ')
    line = line.replace("'", "")
    print(line[1:])


def run_program(file, local_namespace: dict) -> None:
    for line_num, line in enumerate(file.readlines()):
        line = line.strip()  # remove extra whitespace and blank lines
        valid: bool = parse_line(line_num, line, local_namespace)
        if valid:
            pass  # where we will run this line of code


def main() -> None:
    # filename = input()
    filename = 'test.binp'

    global_namespace = {}
    global_namespace['x'] = 10

    assert filename[-5:] == '.binp'

    try:
        run_program(open(filename), global_namespace)
    except FileNotFoundError:
        assert False, "File does not exist"


if __name__ == '__main__':
    main()
