import sys
import dis
from enum import Enum, auto


class Events(Enum):
    CALL = auto()
    LINE = auto()
    RETURN = auto()
    EXCEPTION = auto()


def incrementor(frame, event, arg):
    event = getattr(Events, event.upper())
    if event is Events.LINE:
        program_counter = frame.f_lasti // 2

        buffer = tuple(dis.Bytecode(frame.f_code))
        lastinstr = buffer[program_counter]

        if lastinstr.argval == "goto":
            frame.f_lineno += buffer[program_counter + 1].argval

    return incrementor


sys.settrace(incrementor)


def test():
    print(1, end=",")
    goto(3)
    print(3, end=",")
    goto(3)
    print(2, end=",")
    goto(-3)
    print(4)


test()
