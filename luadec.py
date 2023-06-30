import sys
import pickle
from pathlib import Path

from shared import Chunk
from iter import Iterator
from lua4 import OP, OP_NAME, get_OP, get_B, get_Bx, get_S, get_U, get_A
from lua4 import ASTRoot, ASTClosure, ASTCall, \
    ASTAssignment, ASTPrimitive, ASTTable, ASTMap, ASTCondition


class State:
    def __init__(self):
        self.parameters = []
        self.locals = []
        self.stack = []


def process_closure(it: Iterator, chunk: Chunk, state: State):
    name = ''

    instruction = it.next()
    operator = get_OP(instruction)

    if operator == OP.SETGLOBAL:
        name = chunk.strings[get_B(instruction)]
        it.next()
    else:
        it.prev()

    print(chunk.functions[get_Bx(it.get())].instructions)
    body = process_chunk(chunk.functions[get_Bx(it.get())])

    return ASTClosure(name, state.parameters, body)


def process_call(it: Iterator, chunk: Chunk, state: State):
    args = []
    while state.stack:
        args.append(state.stack.pop())

    if args:
        name = args.pop()
    else:
        name = ASTPrimitive('')

    return ASTCall(
        name.value,
        reversed(args))


def process_assignment(it: Iterator, chunk: Chunk, state: State):
    return ASTAssignment(
        ASTPrimitive('var'),
        ASTPrimitive(0))


def process_set_table(it: Iterator, chunk: Chunk, state: State):
    right = state.stack.pop()
    left = state.stack.pop()

    return ASTAssignment(
        left,
        right)


def process_create_table(it: Iterator, chunk: Chunk, state: State):
    num_entries = get_B(it.get())
    it.next()

    entries = []

    name = state.stack.pop()

    for _ in range(num_entries):
        build_stack(it, chunk, state)
        it.next()

        operator = get_OP(it.get())
        if operator in PROCESS:
            state.stack.append(PROCESS[operator](it, chunk, state))
        else:
            build_stack(it, chunk, state)
        it.next()

        value = state.stack.pop()
        key = state.stack.pop()
        entries.append(ASTAssignment(key, value))

    return ASTTable(
        name.value,
        entries)


def process_map(it: Iterator, chunk: Chunk, state: State):
    return ASTMap(
        'map',
        [ASTPrimitive(0)])


def process_condition(it: Iterator, chunk: Chunk, state: State):
    operator = get_OP(it.get())

    if operator == OP.JMPT:
        condition = f'{state.stack.pop().print()} ~= nil'

    elif operator == OP.JMPF:
        condition = f'{state.stack.pop().print()} == nil'

    elif operator == OP.JMPNE:
        right = state.stack.pop()
        left = state.stack.pop()
        condition = f'{left.print()} ~= {right.print()}'

    elif operator == OP.JMPEQ:
        right = state.stack.pop()
        left = state.stack.pop()
        condition = f'{left.print()} == {right.print()}'

    elif operator == OP.JMPLT:
        right = state.stack.pop()
        left = state.stack.pop()
        condition = f'{left.print()} < {right.print()}'

    elif operator == OP.JMPLE:
        right = state.stack.pop()
        left = state.stack.pop()
        condition = f'{left.print()} <= {right.print()}'

    elif operator == OP.JMPGT:
        right = state.stack.pop()
        left = state.stack.pop()
        condition = f'{left.print()} > {right.print()}'

    elif operator == OP.JMPGE:
        right = state.stack.pop()
        left = state.stack.pop()
        condition = f'{left.print()} >= {right.print()}'

    # elif operator == OP.JMPONT:
    #    value = f'\n'

    # elif operator == OP.JMPONF:
    #    value = f'\n'

    # elif operator == OP.JMP:
    #    value = f'\n'

    else:
        condition = '#TODO condition'

    block = []
    nested_state = State()
    operator = get_OP(it.next())
    while operator != OP.END:
        if operator in PROCESS:
            block.append(PROCESS[operator](it, chunk, nested_state))
        else:
            build_stack(it, chunk, nested_state)
        operator = get_OP(it.next())

    return ASTCondition(condition, block)


PROCESS = {
    OP.CLOSURE:     process_closure,
    OP.CALL:        process_call,
    OP.SETGLOBAL:   process_assignment,
    OP.SETTABLE:    process_set_table,
    OP.CREATETABLE: process_create_table,
    OP.SETMAP:      process_map,
    OP.JMPNE:       process_condition,
    OP.JMPEQ:       process_condition,
    OP.JMPLT:       process_condition,
    OP.JMPLE:       process_condition,
    OP.JMPGT:       process_condition,
    OP.JMPGE:       process_condition,
    OP.JMPT:        process_condition,
    OP.JMPF:        process_condition,
}


def build_stack(it: Iterator, chunk: Chunk, state: State):
    instruction = it.get()
    operator = get_OP(instruction)

    # Get

    if operator == OP.GETGLOBAL:
        value = chunk.strings[get_B(instruction)]

    elif operator == OP.GETLOCAL:
        index = get_B(instruction)

        # Create local variable names (SWBF does not store local variable names)
        while len(state.locals) <= index:
            state.locals.append(f'l{len(state.locals)}')

        value = state.locals[index]

    elif operator == OP.GETDOTTED:
        left = state.stack.pop()
        right = chunk.strings[get_B(instruction)]
        value = f'{left.print()}.{right}'

    # Push

    elif operator == OP.PUSHNIL:
        value = 'nil'

    elif operator == OP.PUSHINT:
        value = get_S(instruction) + 1  # unclear why +1 is necessary

    elif operator == OP.PUSHNUM:
        value = chunk.numbers[get_B(instruction)]

    elif operator == OP.PUSHNEGNUM:
        value = chunk.numbers[get_B(instruction)] * -1

    elif operator == OP.PUSHSTRING:
        value = f'"{chunk.strings[get_B(instruction)]}"'

    # Arithmetic

    elif operator == OP.MULT:
        right = state.stack.pop()
        left = state.stack.pop()
        value = f'({left.print()} * {right.print()})'

    elif operator == OP.ADDI:
        value = f' + {get_B(instruction)}'

    elif operator == OP.ADD:
        right = state.stack.pop()
        left = state.stack.pop()
        value = f'({left.print()} + {right.print()})'

    elif operator == OP.SUB:
        right = state.stack.pop()
        left = state.stack.pop()
        value = f'({left.print()} - {right.print()})'

    else:
        print('#TODO:', OP_NAME[operator])
        return

    state.stack.append(ASTPrimitive(value))


def process_chunk(chunk: Chunk):
    it = Iterator(chunk.instructions)

    #print(f'{chunk.name=}, {chunk.parameters=}, {len(chunk.functions)=}, {chunk.stacks=}, {len(chunk.strings)=}, {len(chunk.numbers)=}')

    state = State()

    root = ASTRoot()

    # Parameter definition at the start of a chunk
    for parameter in range(chunk.parameters):
        state.parameters.append(f'p{parameter}')
        it.next()

    # Local variable definition at the start of a chunk #TODO
    local = 0
    while get_OP(it.get()) == OP.PUSHINT:
        name = f'l{local}'
        value = get_B(it.get())
        state.locals.append(name)
        it.next()
        local += 1

        root += ASTAssignment(ASTPrimitive(name), ASTPrimitive(value))

    try:
        while it:
            operator = get_OP(it.get())
            print('##', OP_NAME[operator], it._pos)

            if operator in PROCESS:
                root += PROCESS[operator](it, chunk, state)

            elif operator == OP.END:  # End of chunk
                pass

            else:
                build_stack(it, chunk, state)

            it.next()

    except StopIteration as e:
        pass
    except Exception as e:
        print(e)

    return root


def debug(chunk: Chunk, level: int = 0):
    def printf(i):
        op = get_OP(i)
        print(
            '{} '
            '{:<15} {:>10} {:>10} {:>10} {:>10} {:>14} {:>20} {:<10}'.format(
                '  ' * level,
                OP_NAME[op], i, get_U(i), get_B(i), get_Bx(i), get_S(i), bin(get_U(i)),
                '' if get_B(i) >= len(chunk.strings) else chunk.strings[get_B(i)]))

    it = Iterator(chunk.instructions)
    while it:
        printf(it.get())

        it.next()

    it.prev()

    printf(it.next())


def main(file: Path):
    chunk = pickle.load(open(file, 'rb'))

    def rec(c: Chunk):
        idx = 0
        for i in Iterator(c.instructions):
            if get_OP(i) == OP.CLOSURE:
                rec(c.functions[idx])
                idx += 1
            print(OP_NAME[get_OP(i)])
    rec(chunk)

    ast = process_chunk(chunk)

    print(
        '{} '
        '{:<15} {:>10} {:>10} {:>10} {:>10} {:>14} {:>20} {:<10}'.format('', 'OP', 'code', 'U', 'B', 'Bx', 'S', 'bits', 'str'))

    debug(chunk)

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
