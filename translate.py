import codecs
import tokenize
from io import BytesIO


class Translator:
    BASE = codecs.lookup("utf8")
    NAMES = ("tr", "translate", "translator")

    def decode(self, stream):
        stream = BytesIO(stream.encode())
        tokens = list(tokenize.tokenize(stream.readline))

        new_tokens = tokens.copy()
        offset = 0
        for index, token in enumerate(tokens):
            if (
                index < len(tokens) - 1
                and token.type == 1
                and tokens[index + 1].type == 3
            ):
                next_token = tokens[index + 1]
                newsrc = token.string + next_token.string
                newstart = next_token.start[0], next_token.start[1] - len(
                    token.string
                )
                new_tokens.pop(index + offset)
                new_tokens[index] = tokenize.TokenInfo(
                    3, newsrc, newstart, next_token.end, next_token.line
                )
                offset -= 1

        for token in new_tokens:
            print(token)

    def get_encoding(self, name):
        if name in self.NAMES:
            return codecs.CodecInfo(name=name, encode=None, decode=self.decode)


def register():
    translator = Translator()
    codecs.register(translator.get_encoding)


if __name__ == "__main__":
    register()
    from textwrap import dedent

    code = dedent(
        """
    a = "abc"
    b = f"abc"
    c = r"abc"
    d = tr"hello"
    e = en"merhaba"
    """
    )

    print(codecs.decode(code, "tr"))
