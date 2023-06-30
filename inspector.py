import sys
import pickle
from shared import Chunk


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Pass one or more \'*.dat\' files as arguments.\n\n')
        exit(1)

    chunk = pickle.load(open(sys.argv[1], 'rb'))
    print(chunk)
