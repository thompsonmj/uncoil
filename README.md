# uncoil

`uncoil` is a command-line tool designed to explore and recursively unfurl the contents of a directory into a single output, either printed to the terminal or saved to a file. It has an option to skip certain file extensions or entire subdirectories, as it works best with text-based files. 

It will produce tree visualization of directories and files and will reveal the contents of files not specified to be skipped. 

This can be useful for navigating large projects, quickly summarizing as well as thoroughly revealing the structure and contents of a project.

It may be useful for providing context of a codebase to a Large Language Model (LLM).

## Installation

`uncoil` can be installed using pip directly from the GitHub repository or by cloning the repo. Choose the method that best suits your needs.

### Direct Installation with `pip`

First, create and activate a virtual environment. For example, with `conda`, run:
```bash
conda create -n myenv -y
conda activate myenv
```

To install the latest version of `uncoil` directly from GitHub, run:

```bash
pip install git+ssh://git@github.com/thompsonmj/uncoil.git
```

Or to install a pinned release version, such as v1.0.1, run:

```bash
pip install git+ssh://git@github.com/thompsonmj/uncoil.git@v1.0.1
```

## Usage
```bash
uncoil -d <directory> [-o <output_file>] [-x <extensions_to_skip,dirs_to_skip>]
```

### Options

- `-d <directory>`: **Required.** The directory you want to process.
- `-o <output_file>`: Optional. Output file to redirect the output into. If not provided, the output will be printed to the console.
- `-x <extensions_to_skip,dirs_to_skip>`: Optional. A comma-separated list of file extensions or subdirectories to skip.

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

For example, see the [examples/](examples/) directory for output of the following command run on the `uncoil` directory itself (which may be out of date):

```bash
uncoil -d . -o examples/uncoil.txt -x .git,.gitignore,LICENSE,.pyc
```
