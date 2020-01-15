# pip install brm
# cp pathstrings.py $(python -m brm)
# python pathstrings_test.py
from brm import TokenTransformer, pattern


class PathStringTransformer(TokenTransformer):

    # p"some/string"
    @pattern("name", "string")
    def fix_path_strings(self, prefix, string):
        if prefix.string != "p":
            return
        return self.quick_tokenize(
            f'__import__("pathlib").Path(f{string.string})', strip=True
        )
