from __future__ import annotations
from datetime import datetime as dt

erased: bool = False

class Logger:
    def __init__(self, name: str, length: int = 80):
        self.name = name
        self.length = length

    def log(self: Logger, message: str, erase: bool = False, newline: bool = True) -> Logger:
        global erased

        header = f'[{dt.now().time()}][{self.name}]'
        message = message.strip() + ' '

        if erase:
            print(f'\r{header} {message :=<{self.length - len(str(header)) - 1}}', end='\n' if newline else '')
        elif erased:
            print(f'\n{header} {message :=<{self.length - len(str(header)) - 1}}', end='\n' if newline else '')
        else:
            print(f'{header} {message :=<{self.length - len(str(header)) - 1}}', end='\n' if newline else '')
        erased = erase

        return self
