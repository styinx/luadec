import sys
import struct
import math
import pickle
from pathlib import Path

from shared import Chunk


def get_int32(it: iter) -> int:
    v = next(it)
    v += (next(it) << 8)
    v += (next(it) << 16)
    v += (next(it) << 24)
    return v


def get_bytes(it: iter, n: int) -> bytearray:
    b = bytearray(n)
    for i in range(n):
        b[i] += next(it)
    return b


def get_bytes_aligned(it: iter, n: int = 1) -> bytearray:
    b = get_bytes(it, n)

    while n % 4 != 0:
        next(it)
        n += 1

    return b


def get_param(it: iter) -> bytearray:
    read_magic(it)
    param_size = get_int32(it)
    return get_bytes_aligned(it, param_size)


def read_magic(it: iter) -> bytearray:
    return get_bytes(it, 4)


def read_lvl_(it: iter, folder: Path):
    chunk_name = read_magic(it).decode('latin-1')
    chunk_size = get_int32(it)

    if chunk_name == 'scr_':
        name, size, chunk = read_scr_(it)

        print(f'{name} ({size} bytes)')
        with open(folder / (name + '.dat'), 'wb') as file:
            pickle.dump(chunk, file)

    elif chunk_name == 'lvl_':
        get_int32(it)
        get_int32(it)

    else:
        get_bytes(it, chunk_size)

    try:
        read_lvl_(it, folder)

    except StopIteration:
        pass

    except Exception as e:
        print(e)


def read_scr_(it: iter) -> (str, int, Chunk):
    name = get_param(it)[:-1].decode('latin-1')
    info = get_param(it)
    body = get_param(it)

    return name, len(body), handle_script(body)


def handle_script(body: bytes) -> Chunk:
    it = iter(body)
    assert (next(it) == 0x1B)  # .
    assert (next(it) == 0x4C)  # L
    assert (next(it) == 0x75)  # u
    assert (next(it) == 0x61)  # a
    assert (next(it) == 0x40)  # @  (4.0)

    endianness = next(it)
    size_int_bytes = next(it)
    size_size_t_bytes = next(it)
    size_instruction_bytes = next(it)
    size_instruction_bits = next(it)
    size_op_bits = next(it)
    size_b_bits = next(it)
    size_test_number_bits = next(it)

    test_number = struct.unpack('f', get_bytes(it, size_test_number_bits))
    assert (math.isclose(test_number == 3.14159265358979323846E8, 0))

    chunk = handle_chunk(it, size_instruction_bytes, size_op_bits, size_b_bits)

    return chunk


def handle_chunk(it, size_instruction_bytes, size_op_bits: int, size_b_bits: int) -> Chunk:
    name_size = get_int32(it)
    name = get_bytes(it, name_size)[:-1].decode('latin-1')

    line = get_int32(it)
    parameters = get_int32(it)
    variadic = get_bytes(it, 1) == 0x01
    stacks = get_int32(it)

    # Locals
    # Note: SWBF does not seem to save local variable names
    num_locals = get_int32(it)
    locals = []
    for i in range(num_locals):
        size = get_int32(it)
        locals.append(get_bytes(it, size))

    # Lines
    num_lines = get_int32(it)
    lines = []
    for i in range(num_lines):
        size = get_int32(it)
        lines.append(get_bytes(it, size))

    # Constants

    # - Strings
    num_strings = get_int32(it)
    strings = []
    for i in range(num_strings):
        size = get_int32(it)
        strings.append(get_bytes(it, size)[:-1].decode('latin-1'))

    # - Numbers
    num_numbers = get_int32(it)
    numbers = []
    for i in range(num_numbers):
        numbers.append(struct.unpack('f', get_bytes(it, 4))[0])

    # - Functions
    num_functions = get_int32(it)
    functions = []
    for i in range(num_functions):
        functions.append(handle_chunk(it, size_instruction_bytes, size_op_bits, size_b_bits))

    # Instruction
    num_instruction = get_int32(it)
    instructions = []
    for i in range(num_instruction):
        instructions.append(get_int32(it))

    return Chunk(name, line, parameters, variadic, stacks, locals, lines, strings, numbers, functions, instructions)


def main(file, folder: Path):
    it = iter(bytes(open(file, 'rb').read()))
    try:
        assert (next(it) == 0x75)  # u
        assert (next(it) == 0x63)  # c
        assert (next(it) == 0x66)  # f
        assert (next(it) == 0x62)  # b

        file_size = get_int32(it)

        read_lvl_(it, folder)

    except StopIteration as e:
        pass

    except Exception as e:
        print(e)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Pass one or more \'*.lvl\' files as arguments.\n\n'
              'Only files containing a \'scr_\' chunk will produce a \'*.dat\' file which contains '
              'a Lua 4.0 program stored in a pickled \'Chunk\' structure which contains the bytecode.')
        exit(1)

    for file in sys.argv[1:]:
        folder = Path(Path(file).stem)
        folder.mkdir(exist_ok=True)
        main(file, folder)
