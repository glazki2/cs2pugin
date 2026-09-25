import os
import subprocess
import sys
import argparse

SOURCE_EXTENSIONS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx")


def reformat_code(file_path):
    if not os.path.isfile(file_path):
        print(f"File {file_path} does not exist.")
        return False

    try:
        subprocess.run(["clang-format", "-i", file_path], check=True)
        print(f"Reformatted {file_path} successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while reformatting {file_path}: {e}")
        return False


def reformat_code_in_directory(directory, ignored_paths):
    for root, directories, files in os.walk(directory):
        directories[:] = [
            name for name in directories
            if os.path.abspath(os.path.join(root, name)) not in ignored_paths
        ]
        for file in files:
            if file.endswith(SOURCE_EXTENSIONS):
                file_path = os.path.join(root, file)
                if os.path.abspath(file_path) not in ignored_paths:
                    reformat_code(file_path)


def main(args):
    parser = argparse.ArgumentParser(
        description="Format C/C++ files with clang-format."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=os.getcwd(),
        help="File or directory to format (default: current directory)",
    )
    parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="PATH",
        help="File or directory to skip; may be specified more than once",
    )
    options = parser.parse_args(args[1:])

    path = os.path.abspath(options.path)
    ignored_paths = {os.path.abspath(item) for item in options.ignore}
    if os.path.isdir(path):
        reformat_code_in_directory(path, ignored_paths)
    else:
        if path not in ignored_paths:
            reformat_code(path)


if __name__ == "__main__":
    main(sys.argv)
