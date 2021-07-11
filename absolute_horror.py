# <no>

import ast
import inspect

from dataclasses import dataclass
from typing import List


class CompileTimeError(ValueError):
    ...

class Rewriter(ast.NodeTransformer):
    
    def rewrite(self, node):
        new_node = self.visit(node)
        return ast.fix_missing_locations(new_node)
        
@dataclass
class ArgRewriter(Rewriter):
    template_name: str
    translation_map: List[ast.expr]

    def visit_Constant(self, node):
        if isinstance(node.value, float):
            numerator, _, denominator = str(node.value).partition('.')
            if numerator == "0":
                template_var_id = int(denominator)
                if template_var_id >= len(self.translation_map):
                    raise CompileTimeError(
                        f"Template {self.template_name} can't access '.{template_var_id}' since "
                        f"it only got '{len(self.translation_map)}' arg"
                    )
            
                arg = self.translation_map[template_var_id]
                return ast.copy_location(arg, node)
        return node

                
class TemplateRewriter(Rewriter):

    def visit_Compare(self, node):
        if len(node.ops) < 2:
            return self.generic_visit(node)
        
        left, *checks, right = node.ops
        if not (
            isinstance(left, ast.Lt)
            and isinstance(right, ast.Gt)
        ):
            return self.generic_visit(node)
        
        
        template_name = node.left.id
        *context_vars, template_args = node.comparators
        
        if not isinstance(template_args, ast.Tuple):
            template_args = ast.copy_location(
                ast.Tuple(elts=[template_args], ctx=ast.Load()),
                template_args
            )

        arg_rewriter = ArgRewriter(template_name, template_args.elts)
        context_args = [
            arg_rewriter.rewrite(context_var)
            for context_var in context_vars
        ]
        if checks:
            context_args = [ast.Compare(context_args[0], checks, context_args[1:])]
            template_args.elts.append(
                ast.Constant(ast.unparse(context_args[0]))
            )

        call = ast.Call(ast.Name(f"__template_{template_name}", ast.Load()), [
            *context_args,
            template_args
        ], keywords=[])
        return ast.copy_location(call, node)

def magic(func):
    source = inspect.getsource(func)
    
    template_rewriter = TemplateRewriter()
    tree = template_rewriter.rewrite(ast.parse(source))

    assert len(tree.body) == 1
    assert isinstance(node := tree.body[0], ast.FunctionDef)
    assert len(node.args.defaults + node.args.kw_defaults) == 0

    assert len(node.decorator_list) == 1
    decorator = node.decorator_list.pop()
    assert isinstance(decorator, ast.Name)
    assert decorator.id == "magic"

    namespace = {}
    exec(
        compile(tree, func.__code__.co_filename, 'exec'),
        func.__globals__,
        namespace
    )
    return namespace.pop(func.__name__)

def __template_Ensure(expr, args):
    return expr

def __template_Assert(expr, args):
    if not expr:
        *args, check = args
        raise AssertionError(f'{check} failed!')
@magic
def foo(x, y):
    x = Ensure<int(.0)>(x)
    Assert<.0 ** 2 == .1>(x, y)
    return x + y

