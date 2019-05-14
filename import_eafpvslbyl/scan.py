import ast
import itertools
import os
from contextlib import suppress
from multiprocessing import Process
from tokenize import open as fopen


class ExtendedVisitor(ast.NodeVisitor):
    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)  # actualy does nothing
        self.filename = filename
        self.count = 0

        self.logs = []


class ImportEAFP(ExtendedVisitor):
    def visit_Try(self, node):
        for handler in node.handlers:
            if isinstance(handler.type, ast.Name) and handler.type.id == "ImportError":
                self.logs.append(f"{self.filename}:{node.lineno}")
                self.count += 1
                break

        return self.generic_visit(node)


class ImportLBYL(ExtendedVisitor):
    def visit_Call(self, node):
        if not (isinstance(node.func, ast.Name) and node.func.id == "find_spec"):
            return self.generic_visit(node)

        self.logs.append(f"{self.filename}:{node.lineno}")
        self.count += 1


def find_py_files(src):
    if not os.path.isdir(src):
        yield os.path.split(src)
    for srcpath, _, fnames in os.walk(src):
        yield from zip(
            itertools.repeat(srcpath),
            filter(lambda fname: fname.endswith(".py"), fnames),
        )


def visit_py_files(src, visitor):
    for file in find_py_files(src):
        with suppress(SyntaxError):
            fname = os.path.join(*file)

            with fopen(fname) as f:
                content = f.read()

            content = content.replace("\r\n", "\n").replace("\r", "\n").strip()
            if not content.endswith("\n"):
                content += "\n"

            tree = ast.parse(content)
            visitor.filename = file[-1]
            visitor.visit(tree)


if __name__ == "__main__":
    path = os.path.dirname(os.__file__)

    for Visitor in ExtendedVisitor.__subclasses__():
        visitor = Visitor()
        visit_py_files(path, visitor)
        with open(
            os.path.join(os.path.dirname(__file__), visitor.__class__.__name__), "w"
        ) as f:
            f.write(f"Total Matches: {visitor.count}\n\n")
            for line in visitor.logs:
                f.write(line + "\n")
