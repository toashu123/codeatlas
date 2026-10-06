import sys
from pathlib import Path

from tree_sitter import Language, Parser
import tree_sitter_python


def parse_file(file_path: str) -> None:
    source = Path(file_path).read_bytes()

    language = Language(tree_sitter_python.language())
    parser = Parser(language)

    tree = parser.parse(source)

    print(f"Parsed: {file_path}")
    print(tree.root_node)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parser.py <python-file>")
        sys.exit(1)

    parse_file(sys.argv[1])
