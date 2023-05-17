class Iterator:
    def __init__(self, values: list):
        self._pos = 0
        self._min = 0
        self._max = len(values)
        self._val = values[0]
        self._values = values

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __bool__(self):
        return self._pos != self._max

    def get(self):
        return self._val

    def next(self):
        self._pos += 1

        if self._pos > self._max:
            raise StopIteration

        self._val = self._values[self._pos - 1]
        return self._val

    def prev(self):
        self._pos -= 1

        self._pos = max(self._min, self._pos)

        self._val = self._values[self._pos]
        return self._val
