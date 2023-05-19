INT_MAX = 2147483647 - 2


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

    def print(self, level: int):
        children = ''
        for child in self.statements:
            children += child.print(level) + '\n'

        return children


class ASTClosure:
    def __init__(self, name: str, statements: iter = None):
        self.name = name

        if not statements:
            self.statements = []
        else:
            self.statements = statements

    def print(self, level: int):
        indent = ASTRoot.INDENT * level

        children = ''
        for child in self.statements:
            children += child.print(level + 1) + '\n'

        return str(
            f'{indent}function {self.name}()\n'
            f'{children}'
            f'{indent}end\n')


class ASTCall:
    def __init__(self, name: str, args: iter = None):
        self.name = name

        if not args:
            self.args = []
        else:
            self.args = args

    def print(self, level: int):
        indent = ASTRoot.INDENT * level
        return f'{indent}{self.name}({", ".join(list(map(str, self.args)))})'


class Assignment:
    def __init__(self, variable, value):
        self._variable = variable
        self._value = value


class Condition:
    def __init__(self, condition):
        pass
