# uncoil

`uncoil` is a command-line tool designed to explore and recursively unfurl the contents of a directory into a single output, either printed to the terminal or saved to a file. It has an option to skip certain file extensions or entire subdirectories, as it works best with text-based files.

It will produce tree visualization of directories and files and will reveal the contents of files not specified to be skipped. 

By default, folders and files that are suspected to provide no useful information (e.g., `.git`, `.venv`, `__pycache__`, etc.) are *hard skipped*, i.e. they are not included in the tree, and their contents are not revealed. Data folders and files which would not provide useful information through their contents but possibly through their presence (e.g. `.jpg`, `.tar`, etc.) are *soft skipped*, i.e. they are shown in the tree, but their contents are not revealed. 

Using the `-x` option, you can specify additional file extensions or directories to *hard skip*.

This can be useful for navigating large projects, quickly summarizing as well as thoroughly revealing the structure and contents of a project.

It may be useful for providing context of a codebase to a Large Language Model (LLM).

## Installation

To install the latest version of `uncoil`, run:

```bash
pip install uncoil
```

## Usage
```bash
uncoil -d <directory> [-o <output_file>] [-x <extensions_to_skip,dirs_to_skip>] [-t <tag>]
```

### Options

```console
usage: uncoil [-h] -d DIRECTORY [-o OUTPUT_FILE] [-x EXCLUDE] [-t TAG]

Process a directory and unfurl its contents.

options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory to process.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Output file to redirect output into.
  -x EXCLUDE, --exclude EXCLUDE
                        Comma-separated list of file extensions or directories to skip.
  -t TAG, --tag TAG     Optional tag to wrap around output. Enter 'none' for no tag.
```

### Examples

1. **Print the unfiltered structure of a directory to the console:**
```bash
uncoil -d directory
```
2. **Print the structure of a directory to the console, skipping certain extensions and subdirectories:**
```bash
uncoil -d directory -x .log,.tmp,.git
```
3. **Save the unfiltered structure of a directory to a file:**
```bash
uncoil -d directory -o output.txt
```
4. **Save the structure of a directory to a file, skipping certain extensions and subdirectories:**
```bash
uncoil -d directory -o output.txt -x .log,.tmp,.git
```

5. **Save the unfiltered structure of a directory to a file, wrapping the output in a custom tag:**
```bash
uncoil -d directory -o output.txt -t "my_project"
```

For example, see the [examples/](examples/) directory for output of the following command run on this `uncoil` repository itself:

```bash
uncoil -d . \
-o examples/uncoil.txt \
-x LICENSE \
-t uncoil_codebase
```
## Development
To develop the package further:

1. Clone the repository and create a branch
2. Install with dev dependencies:
```bash
pip install -e ".[dev]"
```
3. Install pre-commit hook
```bash
pre-commit install
pre-commit autoupdate # optionally update
```
4. Run tests:
```bash
pytest
```
