# A short example to demonstrate the benefits of linear form
# bytecode vs tree walking interpreters to my friend.

import ast
import io
import tokenize
from dataclasses import dataclass
from typing import Iterator, List, Optional, Union


def lex(source: str) -> Iterator[tokenize.TokenInfo]:
    buffer = io.StringIO(source)
    yield from tokenize.generate_tokens(buffer.readline)


class Node:
    ...


@dataclass
class Operation:
    kind: str


@dataclass
class Constant(Node):
    value: Union[str, bool, int, float]


@dataclass
class Identifier(Node):
    name: str


@dataclass
class Sequence(Node):
    elements: List[Node]


@dataclass
class Program(Node):
    blocks: List[Node]


def parse(source: str) -> Program:
    tokens = lex(source)

    def parse_expr(tokens, lookahead):
        if lookahead.exact_type in (tokenize.STRING, tokenize.NUMBER):
            value = ast.literal_eval(lookahead.string)
            return Constant(value)
        elif lookahead.exact_type == tokenize.NAME:
            if lookahead.string in ("true", "false"):
                value = ast.literal_eval(lookahead.string.title())
                return Constant(value)
            else:
                return Identifier(lookahead.string)
        elif lookahead.exact_type == tokenize.LSQB:
            nodes = []
            while True:
                lookahead = next(tokens)
                if lookahead.exact_type == tokenize.RSQB:
                    break
                if node := parse_expr(tokens, lookahead):
                    nodes.append(node)
            return Sequence(nodes)
        elif lookahead.type == tokenize.OP:
            return Operation(lookahead.string)
        elif lookahead.type in (
            tokenize.NEWLINE,
            tokenize.NL,
            tokenize.COMMENT,
            tokenize.ENDMARKER,
        ):
            return None
        else:
            raise SyntaxError(f"Unexpected token: {token.string!r}")

    nodes = []
    while True:
        try:
            if node := parse_expr(tokens, next(tokens)):
                nodes.append(node)
        except StopIteration:
            break

    return Program(nodes)


@dataclass
class Instruction:
    opcode: str
    oparg: Optional[int]


@dataclass
class Bytecode:
    instructions: List[Instruction]


def compile_j(source: str) -> Bytecode:
    def compile_node(node):
        if isinstance(node, Constant):
            yield Instruction("LOAD_LIT", node.value)
        elif isinstance(node, Identifier):
            yield Instruction("CALL_SYM", node.name)
        elif isinstance(node, Operation):
            yield Instruction("CALL_FUN", node.kind)
        elif isinstance(node, Sequence):
            for elt in node.elements:
                yield from compile_node(elt)
            yield Instruction("BUILD_STACK", len(node.elements))

    program = parse(source)
    instructions = []
    for node in program.blocks:
        instructions.extend(compile_node(node))
    return Bytecode(instructions)


print(compile_j("[1 2 + * [dup] [] + + ] * * +"))
