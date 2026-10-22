from dataclasses import dataclass, field

from tree_sitter import Node

from analyser.parser import parse_file


@dataclass
class Definition:
    kind: str
    name: str
    line: int


@dataclass
class Import:
    module: str
    name: str | None
    line: int


@dataclass
class Call:
    name: str
    line: int


@dataclass
class FileFacts:
    definitions: list[Definition] = field(default_factory=list)
    imports: list[Import] = field(default_factory=list)
    calls: list[Call] = field(default_factory=list)


def node_text(node: Node) -> str:
    return node.text.decode("utf-8")


def extract(tree) -> FileFacts:
    facts = FileFacts()

    def visit(node: Node):
        # -------------------------
        # Function definition
        # -------------------------
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")

            if name_node:
                facts.definitions.append(
                    Definition(
                        kind="function",
                        name=node_text(name_node),
                        line=node.start_point[0] + 1,
                    )
                )

        # -------------------------
        # Class definition
        # -------------------------
        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")

            if name_node:
                facts.definitions.append(
                    Definition(
                        kind="class",
                        name=node_text(name_node),
                        line=node.start_point[0] + 1,
                    )
                )

        # -------------------------
        # import x
        # -------------------------
        elif node.type == "import_statement":
            facts.imports.append(
                Import(
                    module=node_text(node),
                    name=None,
                    line=node.start_point[0] + 1,
                )
            )

        # -------------------------
        # from x import y
        # -------------------------
        elif node.type == "import_from_statement":
            facts.imports.append(
                Import(
                    module=node_text(node),
                    name=None,
                    line=node.start_point[0] + 1,
                )
            )

        # -------------------------
        # Function / method call
        # -------------------------
        elif node.type == "call":
            function_node = node.child_by_field_name("function")

            if function_node:
                facts.calls.append(
                    Call(
                        name=node_text(function_node),
                        line=node.start_point[0] + 1,
                    )
                )

        # -------------------------
        # Visit children
        # -------------------------
        for child in node.children:
            visit(child)

    visit(tree.root_node)

    return facts


def print_facts(facts: FileFacts):
    print("=== DEFINITIONS ===")

    for definition in facts.definitions:
        print(
            f"line {definition.line:>4} "
            f"{definition.kind:<8} "
            f"{definition.name}"
        )

    print("\n=== IMPORTS ===")

    for import_item in facts.imports:
        print(
            f"line {import_item.line:>4} "
            f"{import_item.module}"
        )

    print("\n=== CALLS ===")

    for call in facts.calls:
        print(
            f"line {call.line:>4} "
            f"{call.name}"
        )


def main():
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m analyser.extractor <python-file>")
        sys.exit(1)

    file_path = sys.argv[1]

    tree = parse_file(file_path)

    facts = extract(tree)

    print(f"\nExtracted facts from: {file_path}\n")

    print_facts(facts)


if __name__ == "__main__":
    main()
