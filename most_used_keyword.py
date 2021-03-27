import ast
import keyword
import tokenize
from argparse import ArgumentParser
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from pprint import pprint

KEYWORDS = frozenset(keyword.kwlist)


def process_project(project_dir):
    counter = Counter()
    for py_file in project_dir.glob("**/*.py"):
        try:
            stream = tokenize.open(py_file)
            ast.parse(stream.read())
        except (ValueError, SyntaxError):
            continue
        else:
            stream.seek(0)

        counter.update(
            token.string
            for token in tokenize.generate_tokens(stream.readline)
            if token.type == tokenize.NAME
            if token.string in KEYWORDS
        )
        stream.close()

    return counter


def count_keywords(data_dir):
    counter = Counter()
    with ProcessPoolExecutor(max_workers=8) as executor:
        for status, result in enumerate(
            executor.map(process_project, data_dir.iterdir())
        ):
            if status % 10 == 0:
                print(f"{status} projects processed.")
            counter.update(result)

    return counter


def main(args=None):
    parser = ArgumentParser()
    parser.add_argument("data_dir", type=Path)

    options = parser.parse_args(args)
    pprint(count_keywords(options.data_dir))


if __name__ == "__main__":
    main()
