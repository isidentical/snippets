import ast
try:
    import parso

    def _get_error_list(code, version=None):
        grammar = parso.load_grammar(version=version)
        tree = grammar.parse(code)
        return list(grammar.iter_errors(tree))
except ImportError: ...
