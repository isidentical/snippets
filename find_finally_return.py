import ast
import itertools
import os
from contextlib import suppress
from multiprocessing import Process
from pathlib import Path
from tokenize import open as fopen


class ExtendedVisitor(ast.NodeVisitor):
    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.count = 0

        self.logs = []


class FinallyHandler(ExtendedVisitor):
    def visit_Try(self, node):
        if node.finalbody:
            for subnode in node.finalbody:
                for subbernode in ast.walk(subnode):
                    if isinstance(
                        subbernode, (ast.Break, ast.Continue, ast.Return)
                    ):
                        self.count += 1
                        self.logs.append(
                            f"{self.filename}:{subbernode.lineno}"
                        )

        return self.generic_visit(node)


def visit_py_files(src, visitor):
    for file in Path(src).glob("**/*.py"):
        with suppress(SyntaxError):
            with fopen(file) as f:
                content = f.read()

            content = content.replace("\r\n", "\n").replace("\r", "\n").strip()
            if not content.endswith("\n"):
                content += "\n"

            tree = ast.parse(content)
            visitor.filename = file
            visitor.visit(tree)


if __name__ == "__main__":
    path = "/home/batuhan/cpython/Lib"

    for Visitor in ExtendedVisitor.__subclasses__():
        visitor = Visitor()
        visit_py_files(path, visitor)
        print("Total matches:", visitor.count)
        print(*visitor.logs, sep="\n")
