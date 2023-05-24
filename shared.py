class Chunk:
    def __init__(self, name, line: int, parameters: int, variadic: bool, stacks: int,
                 locals: list, lines: list, strings: list, numbers: list, functions: list, instructions):
        self.name = name
        self.line = line
        self.parameters = parameters
        self.variadic = variadic
        self.stacks = stacks
        self.locals = locals
        self.lines = lines
        self.strings = strings
        self.numbers = numbers
        self.functions = functions
        self.instructions = instructions