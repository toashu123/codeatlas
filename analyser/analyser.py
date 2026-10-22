# Its job is to coordinate the existing components.
import sys

from analyser.scanner import discover_python_files
from analyser.parser import parse_file
from analyser.extractor import extract


def analyse_project(root):
    # Step 1: Discover all Python files
    files = discover_python_files(root)

    print(f"Found {len(files)} Python files\n")

    results = {}

    # Step 2: Parse and extract every file
    for file_path in files:
        print(f"Analysing: {file_path}")

        try:
            # Parse the file
            tree = parse_file(str(file_path))

            # Extract definitions, imports and calls
            facts = extract(tree)

            # Store facts against the file
            results[file_path] = facts

        except Exception as error:
            print(f"  Error: {error}")

    return results


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m analyser.analyser <project-directory>")
        sys.exit(1)

    project_root = sys.argv[1]

    results = analyse_project(project_root)

    print("\nAnalysis complete.")
    print(f"Files successfully analysed: {len(results)}")


if __name__ == "__main__":
    main()

