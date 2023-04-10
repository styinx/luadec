class Chunk:
    def __init__(self, name, line: int, parameters: int, variadic: bool, max_stack: int,
                 locals: list, lines: list, strings: list, numbers: list, functions: list, instructions):
        self.name = name
        self.line = line
        self.parameters = parameters
        self.variadic = variadic
        self.max_stack = max_stack
        self.locals = locals
        self.lines = line
        self.strings = strings
        self.numbers = numbers
        self.functions = functions
        self.instructions = instructions