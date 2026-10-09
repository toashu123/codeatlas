"""
CodeAtlas - Week 1: AST fundamentals.

Usage:
    python ast_explorer.py path/to/file.py            # defs + calls
    python ast_explorer.py path/to/file.py --tree     # also dump raw AST

Requires: pip install tree-sitter tree-sitter-python
"""
import sys
from dataclasses import dataclass, field

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


@dataclass
class Definition:
    kind: str          # "function" | "class"
    name: str
    line: int          # 1-based
    parent: str | None # enclosing class/function name, if any


@dataclass
class Call:
    callee: str        # text of the thing being called, e.g. "foo" or "self.bar"
    line: int
    caller: str | None # enclosing function name, None if module level


@dataclass
class FileFacts:
    defs: list[Definition] = field(default_factory=list)
    calls: list[Call] = field(default_factory=list)


def text(node: Node) -> str:
    return node.text.decode("utf8")


def extract(root: Node) -> FileFacts:
    facts = FileFacts()

    def visit(node: Node, scope: list[str], func_scope: str | None):
        if node.type in ("function_definition", "class_definition"):
            name_node = node.child_by_field_name("name")
            name = text(name_node)
            facts.defs.append(
                Definition(
                    kind="function" if node.type == "function_definition" else "class",
                    name=name,
                    line=node.start_point[0] + 1,
                    parent=scope[-1] if scope else None,
                )
            )
            new_func = name if node.type == "function_definition" else func_scope
            for child in node.children:
                visit(child, scope + [name], new_func)
            return

        if node.type == "call":
            fn = node.child_by_field_name("function")
            facts.calls.append(
                Call(callee=text(fn), line=node.start_point[0] + 1, caller=func_scope)
            )
            # keep walking: calls can be nested, e.g. f(g(x))

        for child in node.children:
            visit(child, scope, func_scope)

    visit(root, [], None)
    return facts


def dump_tree(node: Node, depth: int = 0, max_depth: int = 6):
    """Print the raw AST so you can see what tree-sitter actually produces."""
    if not node.is_named or depth > max_depth:
        return
    snippet = text(node).replace("\n", " ")[:40]
    print(f"{'  ' * depth}{node.type}  [{snippet}]")
    for child in node.children:
        dump_tree(child, depth + 1, max_depth)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "rb") as f:
        source = f.read()

    tree = parser.parse(source)

    if "--tree" in sys.argv:
        print("=== RAW AST ===")
        dump_tree(tree.root_node)
        print()

    if tree.root_node.has_error:
        print("warning: file has syntax errors; results may be partial\n")

    facts = extract(tree.root_node)

    print("=== DEFINITIONS ===")
    for d in facts.defs:
        owner = f" (in {d.parent})" if d.parent else ""
        print(f"  line {d.line:>4}  {d.kind:<8} {d.name}{owner}")

    print("\n=== CALLS ===")
    for c in facts.calls:
        who = c.caller or "<module>"
        print(f"  line {c.line:>4}  {who} -> {c.callee}")


if __name__ == "__main__":
    main()