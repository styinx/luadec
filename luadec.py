import sys
import pickle

from shared import Chunk


def get_OP(instruction: int) -> int:
    return instruction & 0x0000003F


def get_U(instruction: int) -> int:
    return (instruction & 0xFFFFFFC0) >> 6


def get_S(instruction: int) -> int:
    return (instruction & 0xFFFFFFC0) >> 6


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


def process_closure(it: iter, chunk: Chunk):
    i = next(it)
    if i == OP.SETGLOBAL:
        name = chunk.strings[get_B(i)]

        print(f'function {name}()')

        for child in chunk.functions:
            process_chunk(child)

        print(f'end')



HANDLE = {
    OP.CLOSURE: process_closure
}


def process_chunk(chunk: Chunk):
    it = iter(chunk.instructions)

    instruction = next(it)
    print(instruction, OP_NAME[get_OP(instruction)])
    try:
        while it:
            if instruction in HANDLE:
                HANDLE[instruction](it, chunk)
            instruction = next(it)
            print(instruction, OP_NAME[get_OP(instruction)])
    except Exception as e:
        pass


def main(file):
    chunk = pickle.load(open(file, 'rb'))

    process_chunk(chunk)


if __name__ == '__main__':
    main(sys.argv[1])
