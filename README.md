# Python Compiler for the Thymio Robot

This compiler generates bytecode to be executed on the Thymio II robot. It takes in python source code (`.py`), generates an AST (Abstract Syntax Tree), creates intemediate code, and outputs the result to the terminal.<br>
[Run the code!](#running-the-code) <br>
or<br>
[Read the documentation!](documentation.pdf)

![thymio_compiler](./thymio_comp.gif)


The source file ([compiler.py](source/compiler.py)) can largely be divided into fivr parts:

1. Constants and Construct definitions:<br>
    This defines several constants and dictionaries used by the Thymio. These include opcodes, and dictionaries for converting between Python operators and Thymio opcodes. It also includes dictionaries for Thymio-specific identifiers, variables, and native function calls. Additionally, they defines the class *HoleCall*, which is used to keep track of "holes" in the code where addresses are yet to be filled in, and scope_flag, which tracks the current scope of the code. Finally, the code sets several variables used to read and store Thymio code.
2. Bytearray manipulation functions:<br>
   sdfdsf
3. Pre-processor:<br>
    asdsd
4. Code generator:<br>
   asdasd
5. Code printer:<br>
   asdasd

The code defines three functions:

preprocessor(x,mode = 0): A function that takes in a x AST node and an optional argument mode. It performs AST transformations and emits bytecode instructions. The AST transformations include sorting the AST nodes and processing decorator_list of function definitions. Bytecode instructions include emitting DC1, DC2, and STOP.
code_finish(): A function that emits a STOP instruction if the stop_flag is zero.
code_gen(x): A recursive function that takes in a x AST node and generates bytecode instructions. The function supports various AST node types such as ast.Pass, ast.Module, ast.Assign, ast.Attribute, ast.Constant, ast.If, ast.Compare, ast.While, ast.Call, and ast.FunctionDef. The bytecode instructions include emitting PUSH, LOAD, JIN, JUMP, and CALLSUB.







This code defines various constants and data structures, including a dictionary to map Python operators to the corresponding operator codes in the target language, a dictionary to map Thymio event names to event identifiers, a dictionary to map Thymio variable names to variable identifiers, and a dictionary to map Thymio non-volatile variables to the corresponding byte offset and identifier.

It also defines a class HoleCall that stores holes in the code that need to be filled in later, for example when calling a function whose address is not yet known. The class has methods to store and retrieve hole addresses and their corresponding call addresses.

The code also initializes various variables, including input_file (the input file to read the code from), code (the compiled code), globals (a dictionary to store global variables), locals (a dictionary to store local variables), globals_n (the number of global variables), locals_n (the number of local variables), word_size (the size of a word in bytes), var_offset (the offset in memory where variables are stored), stop_flag (a flag to indicate whether the program should stop), and scope_flag (the current scope, either globals or locals).

The code defines several helper functions, including error() to print an error message and exit the program, int_to_bytes() to convert an integer to a little-endian byte string, and bytes_to_int() to convert a byte string to an integer.







This code seems to be a Python implementation of a virtual machine that executes code stored in a variable code. The code uses a series of conditional statements to execute different operations based on the current opcode value. The function list_code takes an optional parameter debug that, when set to True, prints a more detailed output of the execution.

The program creates an empty list opcode that will store the string representation of the executed operations. The function then creates a memdict dictionary to store the memory address of each opcode. The program first loops through the code to build the memdict dictionary and determine the size of the global data (globals). The program then loops through the code again to execute each operation.

The code implements the following operations:

LOAD: loads a value from memory and pushes it onto the stack
STORE: pops a value from the stack and stores it in memory
PUSH: pushes a value onto the stack
CALLSUB: calls a subroutine at a memory address
CALLNAT: calls a native function
ADD, SUB, MULT, DIV, MOD: arithmetic operations
LT, GT, LE, GE, EQ, NE: comparison operations
AND, OR: logical operations
NEG: negates a value on the stack
NOT: performs a logical not operation on a value on the stack
JUMP: jumps to a memory address
JIN: jumps to a memory address if the top value on the stack satisfies a certain condition
STOP: stops execution
RET: returns from a subroutine
The code also contains some additional operations to manage the call stack and memory. Overall, the code appears to be a simple virtual machine implementation with a small set of operations.



The Thymio compiler is a software tool that converts high-level programming code into low-level code that can be understood and executed by the Thymio robot.

The compiler consists of multiple components, including a lexer, a parser, and a code generator. The lexer analyzes the input code and breaks it down into tokens. The parser then takes these tokens and constructs a parse tree to represent the syntax of the input code. Finally, the code generator uses the parse tree to produce the low-level code that the Thymio robot can execute.

The Thymio compiler also supports various programming languages, including Python, Blockly, and Aseba. The input code is first translated into an intermediate representation, which is then transformed into the low-level code by the code generator.

Overall, the Thymio compiler is an essential tool for developing software for the Thymio robot, allowing programmers to write high-level code in their preferred language and then translate it into low-level code that can be executed on the robot.

## Running the code
After downloading the repo, go into the [source](/source/) folder, and put your code into the [test_file.py](source/test_file.py) file. There are already many commented examples demonstrating acceptable python code. Then, simply run the [compiler.py](source/compiler.py) script, and it outputs the bytecode into the terminal.<br>
For full details about the compilers abilities, please read the [documentation](documentation.pdf)