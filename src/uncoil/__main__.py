"""
Usage:
  uncoil -d <directory> [-o <output_file>] [-x <extensions_to_skip,dir_to_skip>]

Options:
  -h --help                 Show this screen.
  -d <directory>            Directory to process.
  -o <output_file>          Output file to redirect output into.
  -x <extensions_to_skip>   Comma-separated list of file extensions or directories to skip.
"""

import os
import sys
from docopt import docopt
from rich.console import Console
from rich.tree import Tree

def matches_skip_pattern(file_path, skip_patterns):
    lower_file = file_path.lower()
    return any(skip.lower() in lower_file for skip in skip_patterns)

def unfurl_directory(directory, skip_list):
    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if not matches_skip_pattern(os.path.join(root, d), skip_list)]
        for file in files:
            file_path = os.path.join(root, file)
            if not matches_skip_pattern(file_path, skip_list):
                yield file_path

def create_tree(directory, skip_list):
    tree = Tree(f"Directory Structure: {directory}")
    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if not matches_skip_pattern(os.path.join(root, d), skip_list)]
        path = root.split(os.sep)
        parent = tree
        for part in path[1:]:
            parent = parent.add(part)
        for file in files:
            file_path = os.path.join(root, file)
            if not matches_skip_pattern(file_path, skip_list):
                parent.add(file)
    return tree

def print_file_contents(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
            print(f"==> {file_path} <==")
            print(contents)
            print("\n")  # Adds an extra newline for readability between files
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

def main():
    args = docopt(__doc__)
    directory = args['-d']
    output_file = args.get('-o')
    extensions_to_skip = args.get('-x', '')

    if extensions_to_skip:
        extensions_to_skip = extensions_to_skip.split(',')
    else:
        extensions_to_skip = []

    console = Console(file=open(output_file, 'w') if output_file else sys.stdout)
    tree = create_tree(directory, extensions_to_skip)
    console.print(tree)

    files = unfurl_directory(directory, extensions_to_skip)

    if output_file:
        sys.stdout = open(output_file, 'a')

    try:
        for file_path in files:
            print_file_contents(file_path)
    finally:
        if output_file:
            sys.stdout.close()

if __name__ == '__main__':
    main()
