# Binary Plus Tutorial

## Table of Contents

- [Binary Plus Tutorial](#binary-plus-tutorial)
  - [Table of Contents](#table-of-contents)
  - [Hello World](#hello-world)
  - [Comments](#comments)
  - [Variable Assignment](#variable-assignment)
  - [Printing/Outputting to Console](#printingoutputting-to-console)
  - [Function Declarations](#function-declarations)
  - [Conditionals](#conditionals)
  - [Interactive system](#interactive-system)

## Hello World

All files end with `.binp`. Here is an example `hello_world.binp`:

```binp
output Hello World!
```

To run this program, from the command line, type:

```bash
$ python binp.py path/to/hello_World.binp
 >> Hello World!
```

## Comments

Any line starting with a `$` is ignored. The `$` must be at the start of the line.

```binp
$ here is a couple
$ of lines with comments
$ all of these lines are ignored by the interpreter
```

## Variable Assignment

TODO Write

Syntax is as follows:

```binp
var <type> <variableName> = <value>
```

Variables names follow from Java where the convention is to use camelCase variable names. Variables can start with any letter followed by any letter, number, or an underscore.

Valid types are:
|   type   | name       |
|----------|------------|
| `bool`   | boolean    |
| `int`    | integer    |
| `str`    | string     |
| `func`   | function   |

All assignments must be within a single line (the exception is functions which is [described below](#function-declarations)). Here is an example of some assignments:

```binp
$ Declaring an integer
var int myInteger = 10

$ The right hand side is evaluated so complex expressions can be made
$ Math expressions follow PEMDAS rules
var int mathExpression = (myInteger * 5) / 2

$ Subtraction must be used to declare negative numbers
$ as Binary Plus only has binary operators
$ (otherwise it would be Unary Plus!)
var int negativeNumber = 0 - 10


$ || = or, && = and
var bool myBool = (true || false) && (false || false)


$ Quotes are not needed around strings
$ However, strings must take up a single line
var str hello = hello world!

$ Strings can also use variables
$ since hello = hello world!, greeting = hello world! how are you today?
var str greeting = hello how are you today?

$ Special characters are not supported
$ The string has "\n" within it NOT a newline
var str myString2 = here are some\nwords on a single line


$ Variables can be re-defined (with different types)
var int myVariable = 5
var bool myVariable = false
```

## Printing/Outputting to Console

The `output` command is used to print to standard out. It behaves similarly to Python 2's print statement. Everything after the `output` command is printed to the console. A newline is implicitly added to the end

```binp
$ prints "hello world!" to the screen
output hello world!

$ outputs can include variables
$ This prints out "Hello, Bennett!"
var str name = Bennett
output Hello, name!

$ To escape a variable name surround the word in quotes
$ this prints "the value of retval is 5"
var int retval = 5
output the value of "retval" is retval
```

## Function Declarations

TODO Write

TODO Inner scopes cannot modify outer scopes

## Conditionals

TODO Write

## Interactive system

TODO Write
