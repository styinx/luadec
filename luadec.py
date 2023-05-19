import os.path
import sys
import pickle
from pathlib import Path

from shared import Chunk
from iter import Iterator
from lua4 import OP, OP_NAME, get_OP, get_B, get_S, ASTRoot, ASTClosure, ASTCall


def process_closure(it: Iterator, chunk: Chunk, stack, local_vars):
    name = ''
    statements = []

    operator = it.next()

    if operator == OP.SETGLOBAL:
        name = chunk.strings[get_B(operator)]
    else:
        it.prev()

    for child in chunk.functions:
        statements.append(process_chunk(child))

    operator = it.next()
    if operator != OP.END:
        assert False, 'END operator expected!'

    return ASTClosure(name, statements)


def process_call(it: Iterator, chunk: Chunk, stack, local_vars):
    def map_type(args):
        out = []
        for arg in args:
            if isinstance(arg, (int, float)):
                out.append(str(arg))
            else:
                out.append(f'"{str(arg)}"')
        return out

    return ASTCall(stack[0], map_type(stack[1:]))


def skip(it: Iterator, chunk: Chunk, stack, local_vars):
    pass


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


PROCESS = {
    OP.CLOSURE: process_closure,
    OP.CALL:    process_call
}


SKIP = {
    OP.END: 0
}


def process_chunk(chunk: Chunk):
    it = Iterator(chunk.instructions)

    stack = []
    local_vars = []

    root = ASTRoot()

    # Local variable definition at the start of a chunk
    while get_OP(it.get()) == OP.PUSHINT:
        local = get_B(it.get())
        local_vars.append(local)
        it.next()
    it.prev()

    try:
        for instruction in it:
            operator = get_OP(instruction)

            if operator in PROCESS:
                root += PROCESS[operator](it, chunk, stack, local_vars)
                stack = []
            elif operator in SKIP:
                pass
            else:
                build_stack(it, chunk, stack, local_vars)

    except StopIteration as e:
        pass
    except Exception as e:
        print(e)

    return root


def main(file: Path):
    chunk = pickle.load(open(file, 'rb'))

    ast = process_chunk(chunk)

    script_name = str(file.parent / file.stem) + '.lua'
    print(script_name)

    with open(script_name, 'w') as script:
        script.write(ast.print(0))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Pass one or more \'*.dat\' files as arguments.\n\n'
              'Produces a \'*.lua\' script file.\n'
              'Use \'*\' wildcard for multiple files with a target folder (*.dat mission).')
        exit(1)

    if sys.argv[1][0] == '*':
        files = Path(sys.argv[2]).glob(sys.argv[1])
    else:
        files = sys.argv[1:]

    for file in files:
        main(Path(file))
