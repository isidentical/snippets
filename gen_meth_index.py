import sys
import pyclbr
import tokenize
from collections import defaultdict
from pprint import pprint

from argparse import ArgumentParser
from pathlib import Path

class _LimitedModuleBrowser(pyclbr._ModuleBrowser):
    def _dummy(self, node):
        self.generic_visit(node)

    visit_Import = _dummy
    visit_ImportFrom = _dummy

pyclbr._ModuleBrowser = _LimitedModuleBrowser

def qualified_name(entry):
    if isinstance(entry, pyclbr.Function) and entry.parent is not None:
        return qualified_name(entry.parent) + '.' + entry.name
    else:
        return entry.name

def get_tree(path, module):
    with tokenize.open(path) as stream:
        source = stream.read()

    tree = {}
    pyclbr._create_tree(module, None, path, source, tree, False)    
    return tree

def collect_entries(tree, keys):
    for key in keys:
        entry = tree[key]
        if entry.name.startswith("_"):
            continue
        yield entry

def compare_tree(base_tree, active_tree):
    added, removed = [], []
    common_top_levels = base_tree.keys() & active_tree.keys()
    added.extend(collect_entries(active_tree, active_tree.keys() ^ common_top_levels))
    removed.extend(collect_entries(base_tree, base_tree.keys() ^ common_top_levels))
    for common_entry in common_top_levels:
        if not (
            isinstance(base_class := base_tree[common_entry], pyclbr.Class)
            and isinstance(active_class := active_tree[common_entry], pyclbr.Class)
        ):
            continue
        common_sub_levels = base_class.children.keys() & active_class.children.keys()
        added.extend(collect_entries(active_class.children, active_class.children.keys() ^ common_sub_levels))
        removed.extend(collect_entries(base_class.children, base_class.children.keys() ^ common_sub_levels))
    return added, removed


def generate_index(base_path, active_path):
    module_index = defaultdict(dict)
    for base_file in base_path.glob("**/*.py"):
        file_name = str(base_file.relative_to(base_path))
        active_file = active_path / file_name
        module_name = file_name.replace('/', '.').removesuffix('.py')
        if 'test.' in module_name or '.tests' in module_name or 'encoding' in module_name or 'idle_test' in module_name:
            continue

        print('processing ', module_name)
        try:
            base_tree = get_tree(base_file, module_name)
            active_tree = get_tree(active_file, module_name)
        except (SyntaxError, FileNotFoundError):
            continue
        
        added, removed = compare_tree(base_tree, active_tree)
        if added:
            module_index[module_name]['added'] = added
        if removed:
            module_index[module_name]['removed'] = removed

    for module, status in module_index.items():
        print('module: ', module)
        if added := status.get("added"):
            print("added: ", [qualified_name(entry) for entry in added])
        if removed := status.get("removed"):
            print("removed: ", [qualified_name(entry) for entry in removed])
        
    pprint(module_index)

def main():
    parser = ArgumentParser()
    parser.add_argument("baseline_path", type=Path)
    parser.add_argument("current_path", type=Path)

    options = parser.parse_args()
    generate_index(options.baseline_path, options.current_path)
    
if __name__ == "__main__":
    main()
