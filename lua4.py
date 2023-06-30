INT_MAX = 2147483647 - 2
NL = '\n'


def get_OP(instruction: int) -> int:
    return instruction & 0x0000003F


def get_U(instruction: int) -> int:
    return (instruction & 0xFFFFFFC0) >> 6


def get_S(instruction: int) -> int:
    return ((instruction & 0xFFFFFFC0) - INT_MAX) >> 6


def get_A(instruction: int) -> int:
    return (instruction & 0xFFFF8000) >> 15


def get_B(instruction: int) -> int:
    return (instruction & 0x00007FC0) >> 6


OP_NAME = [
    "END",  # 0b000000, 0
    "RETURN",  # 0b000001, 1

    "CALL",  # 0b000010, 2
    "TAILCALL",

    "PUSHNIL",  # 0b000100, 4
    "POP",

    "PUSHINT",
    "PUSHSTRING",
    "PUSHNUM",  # 0b001000, 8
    "PUSHNEGNUM",

    "PUSHUPVALUE",

    "GETLOCAL",
    "GETGLOBAL",

    "GETTABLE",
    "GETDOTTED",
    "GETINDEXED",
    "PUSHSELF",  # 0b010000, 16

    "CREATETABLE",

    "SETLOCAL",
    "SETGLOBAL",
    "SETTABLE",

    "SETLIST",
    "SETMAP",

    "ADD",
    "ADDI",
    "SUB",
    "MULT",
    "DIV",
    "POW",
    "CONCAT",
    "MINUS",
    "NOT",

    "JMPNE",  # 0b100000, 32
    "JMPEQ",
    "JMPLT",
    "JMPLE",
    "JMPGT",
    "JMPGE",

    "JMPT",
    "JMPF",
    "JMPONT",
    "JMPONF",
    "JMP",

    "PUSHNILJMP",

    "FORPREP",
    "FORLOOP",

    "LFORPREP",
    "LFORLOOP",

    "CLOSURE"  # 0b110000, 48
]


class OP:
    END, RETURN, CALL, TAILCALL, PUSHNIL, POP, PUSHINT, PUSHSTRING, PUSHNUM, PUSHNEGNUM, PUSHUPVALUE, GETLOCAL, \
    GETGLOBAL, GETTABLE, GETDOTTED, GETINDEXED, PUSHSELF, CREATETABLE, SETLOCAL, SETGLOBAL, SETTABLE, SETLIST, \
    SETMAP, ADD, ADDI, SUB, MULT, DIV, POW, CONCAT, MINUS, NOT, JMPNE, JMPEQ, JMPLT, JMPLE, JMPGT, JMPGE, JMPT, \
    JMPF, JMPONT, JMPONF, JMP, PUSHNILJMP, FORPREP, FORLOOP, LFORPREP, LFORLOOP, CLOSURE = range(49)


class ASTPrimitive:
    def __init__(self, value):
        self.value = value

    def print(self, level: int = 0):
        return str(self.value)


class ASTRoot:
    INDENT = '  '

    def __init__(self, statements: iter = None):
        if not statements:
            self.statements = []
        else:
            self.statements = statements

    def __iadd__(self, other):
        self.statements.append(other)
        return self

    def print(self, level: int = 0):
        children = ''
        for child in self.statements:
            children += child.print(level) + '\n'

        return children


class ASTClosure:
    def __init__(self, name: str, parameters: [str], statements: iter = None):
        self.name = name
        self.parameters = parameters

        if not statements:
            self.statements = []
        else:
            self.statements = statements

    def print(self, level: int = 0):
        indent = ASTRoot.INDENT * level

        children = ''
        for child in self.statements:
            children += child.print(level + 1) + '\n'

        return str(
            f'{indent}function {self.name}({",".join(self.parameters)})\n'
            f'{children}'
            f'{indent}end\n')


class ASTCall:
    def __init__(self, name: str, args: [ASTPrimitive] = None):
        self.name = name

        if not args:
            self.args = []
        else:
            self.args = args

    def print(self, level: int = 0):
        indent = ASTRoot.INDENT * level
        return f'{indent}{self.name}({", ".join(list(map(lambda x: x.print(level), self.args)))})'


class ASTAssignment:
    def __init__(self, left: ASTPrimitive, right: ASTPrimitive):
        self.left = left.print()
        self.right = right.print()

    def print(self, level: int):
        indent = ASTRoot.INDENT * level
        return f'{indent}{self.left} = {self.right}'


class ASTCondition:
    def __init__(self, condition: str, block: [ASTPrimitive]):
        self.condition = condition
        self.block = block

    def print(self, level: int):
        indent = ASTRoot.INDENT * level
        subindent = ASTRoot.INDENT * (level + 1)
        return str(
            f'{indent}if {self.condition} then\n{subindent}'
            f'{(NL + subindent).join(list(map(lambda x: x.print(level), self.block)))}'
            f'\n{indent}end')


class ASTTable:
    def __init__(self, variable: str, values: [ASTPrimitive]):
        self.variable = variable
        self.values = values

    def print(self, level: int = 0):
        indent = ASTRoot.INDENT * level
        subindent = ASTRoot.INDENT * (level + 1)
        return str(
            f'{indent}{self.variable} = {{\n{subindent}'
            f'{("," + NL + subindent).join(list(map(lambda x: x.print(level), self.values)))}'
            f'\n{indent}}}\n')


class ASTMap:
    def __init__(self, name: str, values: [ASTPrimitive]):
        self.name = name
        self.values = values

    def print(self, level: int = 0):
        return '#map#'


class ASTArithmeticOperator:
    def __init__(self, left, right, operator: str):
        self.left = left.print()
        self.right = right.print()
        self.op = operator

    def print(self, level: int = 0):
        return f'{self.left} {self.op} {self.right}'
