import ast
import refactor
from refactor import Rule, ReplacementAction

class ReplaceValue(Rule):
    
    REPLACEMENTS = {'age': 10}

    def match(self, node):
        assert isinstance(node, ast.Dict)
        
        for index, key in enumerate(node.keys):
            if isinstance(key, ast.Constant) and isinstance(
                value := node.values[index], ast.Constant
            ):
                key_v, val_v = key.value, node.value
                if key_v in REPLACEMENTS and node.value != REPLACEMENTS[key_v]:
                    return ReplacementAction(
                        value, 
                        ast.Constant(REPLACEMENTS[key_v])
                    )

if __name__ == "__main__":
    refactor.run()
