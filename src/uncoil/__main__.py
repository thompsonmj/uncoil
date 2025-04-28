import os
import sys
import argparse
from rich.console import Console
from rich.tree import Tree
import fnmatch

from uncoil.config.hard_ignore import HARD_IGNORE_PATTERNS
from uncoil.config.soft_ignore import SOFT_IGNORE_PATTERNS
import logging

def matches_skip_pattern(file_path, skip_patterns):
    lower_file = file_path.lower()
    return any(skip.lower() in lower_file for skip in skip_patterns)

def is_soft_ignored(file_path, soft_patterns):
    p = file_path.lower()
    return any(fnmatch.fnmatch(p, pat.lower()) for pat in soft_patterns)

def unfurl_directory(directory, skip_list):
    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if not matches_skip_pattern(os.path.join(root, d), skip_list)]
        for file in files:
            file_path = os.path.join(root, file)
            if not matches_skip_pattern(file_path, skip_list):
                yield file_path

def create_tree(directory, skip_list):
    # Figure out which files will actually be shown
    visible_files = set(unfurl_directory(directory, skip_list))

    # Build the set of all dirs that contain at least one visible file
    visible_dirs = {os.path.abspath(directory)}
    for fp in visible_files:
        cur = os.path.abspath(os.path.dirname(fp))
        while cur not in visible_dirs:
            visible_dirs.add(cur)
            if cur == os.path.abspath(directory):
                break
            cur = os.path.dirname(cur)

    # Now walk, only keeping dirs in visible_dirs
    tree = Tree(f"Directory Structure: {directory}")
    node_map = {os.path.abspath(directory): tree}

    for root, dirs, files in os.walk(directory, topdown=True):
        abs_root = os.path.abspath(root)

        # Drop any hard-skipped dir OR any dir not in visible_dirs
        pruned_dirs = []
        for d in dirs:
            abs_d = os.path.join(abs_root, d)
            if matches_skip_pattern(abs_d, skip_list):
                continue
            if abs_d not in visible_dirs:
                continue
            pruned_dirs.append(d)
        dirs[:] = pruned_dirs

        parent = node_map[abs_root]
        # Add each remaining dir as a branch
        for d in dirs:
            abs_d = os.path.join(abs_root, d)
            node_map[abs_d] = parent.add(d)

        # Add each file that isn’t hard-skipped
        for f in files:
            abs_f = os.path.join(abs_root, f)
            if not matches_skip_pattern(abs_f, skip_list):
                parent.add(f)

    return tree

def print_file_contents(file_path, console, soft_patterns):
    try:
        console.print(f"==> {file_path} <==")
        if is_soft_ignored(file_path, soft_patterns):
            console.print("[contents ignored]\n", markup=False)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                contents = f.read()
            console.print(contents, markup=False)
            console.print("\n")
    except Exception as e:
        console.print(f"Error reading {file_path}: {e}")

def main():

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logger = logging.getLogger(__name__)

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
    tag_keyword = args.tag

    # Initialize Console
    if output_file:
        try:
            # Ensure the path to the output file exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            file_handle = open(output_file, 'w', encoding='utf-8')
        except Exception as e:
            print(f"Error opening output file {output_file}: {e}")
            sys.exit(1)
        console = Console(file=file_handle)
    else:
        console = Console()

    hard_patterns = list(HARD_IGNORE_PATTERNS)

    # If the user passed -o, add that exact path
    if output_file:
        abs_out = os.path.abspath(output_file)
        hard_patterns.append(abs_out)

        # also ignore by name wherever it appears
        out_name = os.path.basename(output_file)
        if out_name not in hard_patterns:
            logger.info(f"Automatically hard-ignoring output file name '{out_name}' everywhere")
            hard_patterns.append(out_name)

    # Now consume -x/--exclude flags
    cli_excludes = args.exclude.split(',') if args.exclude else []
    for pat in cli_excludes:
        if pat in hard_patterns:
            logger.info(f"Ignoring duplicate pattern '{pat}' (already in defaults)")
        else:
            hard_patterns.append(pat)

    soft_patterns = list(SOFT_IGNORE_PATTERNS)

    # Handle optional tags, with 'none' meaning no tags
    if tag_keyword.lower() != 'none':
        opening_tag = f"<{tag_keyword}>"
        closing_tag = f"</{tag_keyword}>"
        console.print(opening_tag)

    # Create and print the directory tree
    tree = create_tree(directory, hard_patterns)
    console.print(tree)
    console.print("\n")

    # Unfurl files and print their contents
    files = unfurl_directory(directory, hard_patterns)

    try:
        for file_path in files:
            print_file_contents(file_path, console, soft_patterns)
        
        if tag_keyword.lower() != 'none':
            console.print(closing_tag)
    finally:
        if output_file:
            file_handle.close()

if __name__ == '__main__':
    main()
