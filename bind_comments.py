import ast
import io
import tokenize
from argparse import ArgumentParser

from typing import Optional, List, Iterator
from collections import namedtuple
from pprint import pprint

Comment = namedtuple("Comment", ["lineno", "text"])


def get_comments(source: str) -> Iterator[Comment]:
    buffer = io.StringIO(source)
    for token in tokenize.generate_tokens(buffer.readline):
        if token.type == tokenize.COMMENT:
            assert token.start[0] == token.end[0]
            yield Comment(token.start[0], token.string)


def main(argv: Optional[List[str]] = None) -> None:
    parser = ArgumentParser()
    parser.add_argument("file")

    options = parser.parse_args(argv)
    with tokenize.open(options.file) as stream:
        source = stream.read()

    print("Comments: ")
    pprint(list(get_comments(source)))


if __name__ == "__main__":
    main()
