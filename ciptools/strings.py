import re
from io import TextIOBase

# compile this for performance later in the module
NULL_TERMINATOR = re.compile(r"(?<!\\)\\u0000")


# this function was taken from here: https://hakibenita.com/fast-load-data-python-postgresql
class StringIteratorIO(TextIOBase):
    def __init__(self, i):
        self.i = i
        self.buffer = ""

    def readable(self) -> bool:
        return True

    def _read_one(self, n: int = None) -> str:
        while not self.buffer:
            try:
                self.buffer = next(self.i)
            except StopIteration:
                break
        ret = self.buffer[:n]
        self.buffer = self.buffer[len(ret):]
        return ret

    def read(self, n: int = None) -> str:
        line = []

        if n is None or n < 0:
            while True:
                # read the entire thing
                m = self._read_one()
                if not m:
                    break
                line.append(m)
        else:
            while n > 0:
                # read some portion
                m = self._read_one(n)
                if not m:
                    break
                n -= len(m)
                line.append(m)

        return "".join(line)


def replace_null_terminators(text: str, replacement: str = r""):
    return NULL_TERMINATOR.sub(replacement, text) if text is not None else None


def sanitize(text):
    if text is None:
        return None

    from html import escape
    return escape(str(text))


def unsanitize(text):
    if text is None:
        return None

    from html import unescape
    return unescape(str(text))
