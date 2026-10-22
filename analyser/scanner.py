from pathlib import Path


def discover_python_files(root):
    IGNORED_DIRS = {
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    "node_modules",
    }
    root = Path(root)

    if not root.exists():
        raise FileNotFoundError(f"Directory does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    return [ 
        path 
        for path in root.rglob("*.py") 
        if path.is_file() 
        and not any(part in IGNORED_DIRS for part in path.parts) 
    ]


def main():
    # Step 1: Specify the project directory
    project_root = input("Enter project directory path: ")

    # Step 2: Discover Python files
    try:
        python_files = discover_python_files(project_root)

        # Step 3: Display the total number of files
        print(f"\nFound {len(python_files)} Python files\n")

        # Step 4: Display each discovered file
        for file_path in python_files:
            print(file_path.relative_to(project_root))

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
