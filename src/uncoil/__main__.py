import os
import sys
import argparse
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
    node_map = {directory: tree}

    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if not matches_skip_pattern(os.path.join(root, d), skip_list)]
        
        parent_node = node_map[root]

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not matches_skip_pattern(dir_path, skip_list):
                node_map[dir_path] = parent_node.add(dir)

        for file in files:
            file_path = os.path.join(root, file)
            if not matches_skip_pattern(file_path, skip_list):
                parent_node.add(file)  

    return tree

def print_file_contents(file_path, console):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
            console.print(f"==> {file_path} <==")
            console.print(contents, markup=False)
            console.print("\n")  # Adds an extra newline for readability between files
    except Exception as e:
        console.print(f"Error reading {file_path}: {e}")

def main():
    # Set up argument parsing using argparse
    parser = argparse.ArgumentParser(
        description='Process a directory and unfurl its contents.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-d', '--directory', required=True, help='Directory to process.')
    parser.add_argument('-o', '--output_file', help='Output file to redirect output into.')
    parser.add_argument('-x', '--exclude', help='Comma-separated list of file extensions or directories to skip.')
    parser.add_argument('-t', '--tag', default='codebase', help="Optional tags to wrap around output. E.g. <tag> ... </tag>. Enter 'none' (without quotes) for no tag.")
    
    args = parser.parse_args()
    
    directory = args.directory
    output_file = args.output_file
    extensions_to_skip = args.exclude.split(',') if args.exclude else []
    tag_keyword = args.tag

    # Initialize Console
    if output_file:
        try:
            file_handle = open(output_file, 'w', encoding='utf-8')
        except Exception as e:
            print(f"Error opening output file {output_file}: {e}")
            sys.exit(1)
        console = Console(file=file_handle)
    else:
        console = Console()

    # Handle optional tags, with 'none' meaning no tags
    if tag_keyword.lower() != 'none':
        opening_tag = f"<{tag_keyword}>"
        closing_tag = f"</{tag_keyword}>"
        console.print(opening_tag)

    # Create and print the directory tree
    tree = create_tree(directory, extensions_to_skip)
    console.print(tree)
    console.print("\n")

    # Unfurl files and print their contents
    files = unfurl_directory(directory, extensions_to_skip)

    try:
        for file_path in files:
            print_file_contents(file_path, console)
        
        if tag_keyword.lower() != 'none':
            console.print(closing_tag)
    finally:
        if output_file:
            file_handle.close()

if __name__ == '__main__':
    main()
