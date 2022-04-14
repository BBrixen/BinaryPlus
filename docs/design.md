# Design Decisions

TODO Write

## Bennett's Notes
 - Functions were fairly difficult to implement. They are essentially stored as their own list of lines for running a program. When you create a function, it will map the name of the function to the lines inside the function. Then, when you call the function it will just begin running a new binary plus program, which consists of the function lines. 
 - This means that a binary plus program takes in a namespace of variables and can return something. For the outer most scope, this does not matter since we are dealing with a mostly empty global namespace and we do not care about return types
 - Function types and returns are enforced by the function itself
 - If statements were honestly not that difficult. I just needed to add a new parameter when searching through lines to determine if we want to execute or not. When the if statement did not trigger, we could set execute=False, and thus ignore all the lines inside the if statement
 - The above applies to else statements, we just toggle execute to either True or False depending on the original condition
 - While loops were annoying. They should always bring the user back up to the stop to re-evaluate the expression
 - To do this, I had to make sure that EVERY time we parsed and executed a line, it would return a new line number to move onto
 - Most of the time this line number is just 1 more than the previous line number, but for while loops we had to keep track of the line number which marked the start, and instead we would return the starting line number
 - The most fun part of programming this, for me, was definitely functions. Getting those working, along with taking parameters and returning values, was really fun, and I surprisingly did not have that much of a problem implementing it all, after I wrapped my head around a good way to store and execute them.
 - Nested function calls were a bit of a pain. Nested function definitions were quite easy. The way I set up function definitions at first worked very well, and I could nest them immediately. But nested function calls were tough. Being able to call a line like `var int x = func1(1 + 2, func2(x, func1(1, 2), y))` took a really long time and far too much trouble
 - The section of code that I had to keep changing over and over again was string creation. Being able to loop through the string and replace variables with their values had to change basically every time I added a new feature. I had a really good version at the start, but as we added more it kept breaking. We have settled on what I would consider a worse version, but at least it works for all variables and functions. The sad part is we cannout output function returns, instead we have to store those into another variable and output the variable. I definitely could fix this to be better, but then it would probably break some other section and it is not worth my time anymore
 - 