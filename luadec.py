import sys
import pickle

from shared import Chunk
from iter import Iterator

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


def printf(*args, indent=2):
    print(' ' * indent, *args, end=' ')


def process_closure(it: Iterator, chunk: Chunk, stack, local_vars):
    operator = it.next()

    if operator == OP.SETGLOBAL:
        name = chunk.strings[get_B(operator)]
        printf(f'function {name}()\n')
    else:
        it.prev()
        printf(f'function ()\n')

    for child in chunk.functions:
        process_chunk(child)

    operator = it.next()
    if operator == OP.END:
        printf(f'end')


def process_call(it: Iterator, chunk: Chunk, stack, local_vars):
    def map_type(args):
        out = []
        for arg in args:
            if isinstance(arg, (int, float)):
                out.append(str(arg))
            else:
                out.append(f'"{str(arg)}"')
        return out

    printf(f'{stack[0]}({", ".join(map_type(stack[1:]))})\n')


def build_stack(it: Iterator, chunk: Chunk, stack, local_vars):
    instruction = it.get()
    operator = get_OP(instruction)

    if operator == OP.GETGLOBAL:
        stack.append(chunk.strings[get_B(instruction)])
    elif operator == OP.GETLOCAL:
        stack.append(local_vars[get_B(instruction) - 1])  # index starts from 1 and not 0
    elif operator == OP.PUSHINT:
        stack.append(get_S(instruction) + 1)  # unclear why +1 is necessary
    elif operator == OP.PUSHNUM:
        stack.append(chunk.numbers[get_B(instruction)])
    elif operator == OP.PUSHNEGNUM:
        stack.append(chunk.numbers[get_B(instruction)] * -1)
    elif operator == OP.PUSHSTRING:
        stack.append(chunk.strings[get_B(instruction)])
    else:
        print('#TODO:', OP_NAME[operator])


HANDLE = {
    OP.CLOSURE: process_closure,
    OP.CALL: process_call
}


def process_chunk(chunk: Chunk):
    it = Iterator(chunk.instructions)
    stack = []
    local_vars = []

    # Local variable definition at the start of a chunk
    while get_OP(it.get()) == OP.PUSHINT:
        local = get_B(it.get())
        local_vars.append(local)
        it.next()
    it.prev()

    try:
        for instruction in it:
            operator = get_OP(instruction)

            if operator in HANDLE:
                HANDLE[operator](it, chunk, stack, local_vars)
                stack = []
            else:
                build_stack(it, chunk, stack, local_vars)

    except StopIteration as e:
        pass
    except Exception as e:
        print(e)


def main(file):
    chunk = pickle.load(open(file, 'rb'))

    process_chunk(chunk)


if __name__ == '__main__':
    main(sys.argv[1])
