# Binary Plus Tutorial

Binary Plus is an **interpreted language** meaning the program will evaluate your `.binp` file line-by-line. Along with this tutorial, we have many various valid and invalid program examples within the `valid_programs/` and `invalid_programs/` folders.

As the name suggests, the only operators that are supported are binary operators (two arguments required).

## Video Tutorial

Bennett has made a video tutorial that covers many of the topics discussed here. [Click here to go to the video](https://www.youtube.com/watch?v=UMEBoMbGG5w)

Note: If you have pycharm installed, and you want to use the syntax highlighting that I used in my video, follow these steps.
 - Make a copy of your current color scheme configuration: `File > Settings > Editor > Color Scheme > Gear icon > Export > Color scheme plugin (.jar)`
 - Save this copy somewhere, you might want it later
 - Download the color scheme I provided for you: `Binary Plus zip > docs > binp_colors.jar`
 - Import the color scheme I provided: `File > Settings > Editor > Color Scheme > Gear icon > Import > follow the steps to import the file I provided`
 - Open any pycharm and make a file ending in `.binp` and begin typing. It should highlight your syntax.
 - When you want to revert to your old color scheme (if you even want to, personally I think my color scheme is amazing and you should try it): `File > Settings > Editor > Color Scheme > Gear icon > Import > follow the steps to import the file you created at the beginning`

## Table of Contents

- [Binary Plus Tutorial](#binary-plus-tutorial)
  - [Video Tutorial](#video-tutorial)
  - [Table of Contents](#table-of-contents)
  - [Hello World](#hello-world)
  - [Comments](#comments)
  - [Variable Assignment](#variable-assignment)
  - [Printing/Outputting to Console](#printingoutputting-to-console)
  - [Function Declarations](#function-declarations)
  - [Conditionals and Loops](#conditionals-and-loops)
  - [User Input](#user-input)
    - [The `input` command](#the-input-command)
    - [Command Line Arguments](#command-line-arguments)
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


$ || is the OR operator, && is the AND operator
$ Since the language only has binary operators, there is no
$ negation operator. A negation function can be made if this is needed.
var bool myBool = (true || false) && (false || false)

$ true, True, false, and False are valid boolean terms
var bool myBool2 = (True && true) || (false && False)


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

The `output` command is used to print to standard out. It behaves similarly to Ruby's `puts` command. The major difference is the quotes around the string is not needed. `output` also has the feature of finding variables within your string and replacing them in the output. A newline is implicitly added to the end of the string.

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
output the value of 'retval' is retval
```

## Function Declarations

Functions are written slightly differently than most languages. To create a function, we first create an anonymous function which we then assign a name to (via variable assignment)

```
var <return type> func <function name> = (<arguments>) =>
    <code>
end <function name>
```

Possible return types are `bool`, `int`, `str`, or `null` (akin to `void` in Java).

Functions have their own variable scope that is separate from the "global" scope. Functions definitions can also be nested like in Python. Do note that a function can only modify it's own scope (it is unable to modify parent scopes).

Here are a few function examples:

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

## Conditionals and Loops

Binary Plus supports `if` conditions and `while` loops. Here is the general syntax for them:

```binp
if (<boolean condition>) =>
    <code if condition is true>
else =>
    <code if the condition is false>
end

$ An if condition with the else block omitted
if (<boolean condition>) =>
    <code if condition is true>
end

while (<boolean conditoin>) =>
    <code if condition is true>
else =>
    <code that runs once the condition is false>
end

$ A while loop with the else block omitted
while (<boolean conditoin>) =>
    <code if condition is true>
end
```

## User Input

User input can be obtained in two ways

1. The `input` command
2. Command line arguments

### The `input` command

The input command allows for keyboard input.

```binp
var str userString = input

$ the user input is automatically casted to the variable type
var int userInteger = input
var bool userBoolean = input
```

### Command Line Arguments

The global namespace has the `ARG_COUNT` variable defined that gives the number of command line arguments passed in to the program. Each argument can then be accessed via `ARG_X` where `X` is the argument index (indexing is 0-based). Here is an example using `valid_programs/arguments.binp`:

```bash
$ ./binp.py valid_programs/arguments.binp
 >> This program expects that the file be called with three arguments like so:
 >> python binp.py arg1 arg2 arg3

$ ./binp.py valid_programs/arguments.binp quick brown fox
 >> Number of arguments: 3
 >> =======================
 >> first arg: quick
 >> second arg: brown
 >> third arg: fox
```

In the above example, "quick" is `ARG_0`, "brown" is `ARG_1` and "fox" is `ARG_2`

## Interactive system

Just like Python, the Binary Plus file can be executed without passing a file to run the interactive system. This allows you to test out Binary Plus code without having to write it in a file. `Ctrl-C` can be used to terminate the interactive system.
