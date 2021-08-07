import tokenize
from collections import defaultdict
from itertools import chain
from dataclasses import dataclass

@dataclass
class Change:
    value: str
    lineno: int
    col_offset: int

def shift_tokens(tokens, start, offset):
    for index, token in enumerate(tokens[start:]):
        start_line, start_col, end_line, end_col = *token.start, *token.end
        tokens[start + index] = token._replace(
            start=(start_line, start_col + offset),
            end=(end_line, end_col + offset)
        )
    
def parse(stream, changes):
    token_groups = defaultdict(list)
    for token in tokenize.generate_tokens(stream.readline):
        token_groups[token.start[0]].append(token)

    offset_map = defaultdict(int)
    for change in changes:
        token_group = token_groups[change.lineno]
        start_token, end_token = None, None
        for index, token in enumerate(token_group):
            if token.start[1] == change.col_offset + offset_map[change.lineno]:
                start_token = token
                if token_group[index + 1].string in '+-' and token_group[index + 2].type == tokenize.NUMBER:
                    end_token = token_group[index + 2]
                else:
                    end_token = start_token
        
        offset = len(change.value) - end_token.end[1]
        token_group[index] = token._replace(
            string=change.value,
            end=(token.end[0], len(change.value))
        )
        shift_tokens(token_group, index + 1, offset)
        offset_map[change.lineno] += offset
    
    tokens = chain.from_iterable(token_groups.values())
    return tokenize.untokenize(tokens)

with open('dvc/utils/serialize/_py.py') as stream:
    print(parse(stream, [
        Change('bruh', 123, 4)
    ]))
