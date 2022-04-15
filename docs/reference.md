# Reference

Here are all Binary Plus language definitions in one convenient place. To see how to use these, see `docs/tutorial.md`

- [Reference](#reference)
  - [Variable definition](#variable-definition)
  - [Integer operations](#integer-operations)
  - [Boolean operations](#boolean-operations)
  - [Function definition](#function-definition)
  - [While Loop](#while-loop)
  - [If condition](#if-condition)
  - [Input/Output](#inputoutput)

## Variable definition

|   type   | name       | valid options                     |
|----------|------------|-----------------------------------|
| `bool`   | boolean    | `true`, `True`, `false`, `False`  |
| `int`    | integer    | any positive number               |
| `str`    | string     | not surrounded by quotes          |
| `func`   | function   |                                   |

```binp
var str userString = hello world!

var bool x = true && True
```

> The `int_negate()` function can be used to create negative numbers. If you want `-4`, you can call `int_negate(4)`

> The `bool_negate()` function can be used to negate a boolean expression.
If variable `x` holds `True`, calling `bool_negate(x)` returns `False`.

## Integer operations

| symbol | description |
|--------|-------------|
|   `+`  | boolean     |
|   `-`  | integer     |
|   `*`  | string      |
|   `/`  | function    |

Operation precidence (highest to lowest)

1. Parenthesis
2. Division/Multiplication
3. Addition/Subtraction

> The `int_negate()` function can be used to create negative numbers. If you want `-4`, you can call `int_negate(4)`

## Boolean operations

| symbol  | description |
|---------|-------------|
|   `||`  |      or     |
|   `-`   |      and    |

> The `bool_negate()` function can be used to negate a boolean expression.
If variable `x` holds `True`, calling `bool_negate(x)` returns `False`.

## Function definition

```binp
$ A function which takes no arguments and returns 5
var int func five = () =>
    return 5
end five

var int myValue = five()
output myValue


$ Return the max of two integers
var int max = (int a, int b) =>
    if (a < b) =>
        return b
    end

    return a
end max
```

Functions can return `bool`, `int`, `str`, or `null`

## While Loop

```binp
$ Print the first 12 fibonacci numbers
var int i = 0
while (i < 12) =>
    output i
    var int i = i + 1
end
```

## If condition

```binp
if (True) =>
    output "the true condition is running"
else =>
    output "oh we are in the false condition now"
end
```

## Input/Output

```binp
$ print to the screen
output Hello World!

$ Get a line of input from the useer
var str phrase = input
output phrase

$ Quotes can be used to escape variable insertion
var int hello = 1
output why "hello" there!
```

Command line arguments can be gotten via the global variables `ARG_X` where `X` is the index of the argument (first argument starts at 0). `ARG_COUNT` can be used to find out the number of arguments received.
