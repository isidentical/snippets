import ast
from dis import Bytecode
from queue import SimpleQueue
from io import StringIO
from logging import getLogger as logger
from types import CodeType

CODE_FIELDS = (
    "argcount",
    "posonlyargcount",
    "kwonlyargcount",
    "nlocals",
    "stacksize",
    "flags",
    "code",
    "consts",
    "names",
    "varnames",
    "filename",
    "name",
    "firstlineno",
    "lnotab",
    "freevars",
    "cellvars",
)

def assemble(*instrs):
    buf = StringIO()
    for op, arg in instrs:
        buf.write(chr(dis.opmap[op]) + chr(arg or 0))

    return bytes(ord(char) for char in buf.getvalue())

def reassemble_code(kod, **options):
    fields = {f"co_{field}": getattr(kod, f"co_{field}") for field in CODE_FIELDS}
    fields.update(options)
    print(fields)
    return CodeType(**fields)

class Compiler(ast.NodeVisitor):
    def visit(self, *args, **kwargs):
        self.instrset = []
        self.consts = []
        super().visit(*args, **kwargs)
        
        code = assemble(*self.instrset)
        return reassemble_code((lambda: None).__code__, co_code = code, co_consts = self.consts)

    def visit_Const(self, node):
        self.consts.append(node.value)
        self.instrset.append('LOAD_CONST', self.consts.index(node.value))

class VM:
    def __init__(self):
        self._stack = SimpleQueue()
        self._logger = logger()

    def run(self, code):
        buf = Bytecode(code)
        for instr in buf:
            self.dispatch_instr(instr)

    def dispatch_instr(self, instr):
        name = instr.opname.lower()
        if (method := getattr(self, name)):
            method(instr)
        else:
            self._logger.warning(f"Unhandled instruction: {name}")
    
    def load_const(self, instr):
        self._stack.put(instr.argval)
        
if __name__ == '__main__':
    compiler = Compiler()
    vm = VM()
    while True:
        code = input('code > ')
        code = ast.parse(code)
        code = compiler.visit(code)
        vm.run(code)
