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

    def __str__(self):
        def p(chunk: Chunk, indent: int = 0):
            ind = '  ' * indent
            functions = '' if not chunk.functions else ''.join([p(x, indent + 1) for x in chunk.functions])
            return '{}{} ({}) L:{} v:{} S:{}\n' \
                   '{}- Locals       {}\t{}\n' \
                   '{}- Lines        {}\t{}\n' \
                   '{}- Strings      {}\t{}\n' \
                   '{}- Numbers      {}\t{}\n' \
                   '{}- Instructions {}\t{}\n' \
                   '{}- Functions    {}\t{}\n' \
                   '{}'.format(
                ind, chunk.name, chunk.parameters, chunk.line, chunk.variadic, chunk.stacks,
                ind, len(chunk.locals), '', #chunk.locals,
                ind, len(chunk.lines), '',  # chunk.lines,
                ind, len(chunk.strings), '',  # chunk.strings,
                ind, len(chunk.numbers), '',  # chunk.numbers,
                ind, len(chunk.instructions), '',  # chunk.instructions
                ind, len(chunk.functions), '',  # chunk.functions
                functions
            )

        return p(self)
