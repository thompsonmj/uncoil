from io import StringIO
from rich.console import Console
import sys
from unittest import mock

import pytest

from src.uncoil.__main__ import (
    unfurl_directory,
    create_tree,
    print_file_contents,
    is_soft_ignored,
    matches_skip_pattern,
    main,
)
from uncoil.config.hard_ignore import HARD_IGNORE_PATTERNS
from uncoil.config.soft_ignore import SOFT_IGNORE_PATTERNS

@pytest.fixture
def sample_directory(tmp_path):
    """
    Create a sample directory structure for testing.
    """
    # Create directories
    (tmp_path / "src" / "uncoil").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "examples").mkdir()
    
    # Create files
    files = {
        "README.md": "# Sample README",
        "pyproject.toml": "requires = ['pytest']",
        "src/uncoil/__init__.py": "",
        "src/uncoil/__main__.py": "",
        "tests/__init__.py": "",
        "tests/test_main.py": "",
        "examples/uncoil.txt": "Sample output"
    }
    
    for file_path, content in files.items():
        file = tmp_path / file_path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)
    
    # Create skipped directories and files
    (tmp_path / ".git").mkdir()
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / ".venv").mkdir()
    (tmp_path / "LICENSE").write_text("MIT License")
    
    return tmp_path

def test_matches_skip_pattern():
    """
    Test the matches_skip_pattern function.
    """
    assert matches_skip_pattern(".git/config", [".git", ".pyc"])
    assert matches_skip_pattern("src/uncoil/__pycache__/file.pyc", [".git", ".pyc"])
    assert matches_skip_pattern("README.md", ["README"])
    assert not matches_skip_pattern("src/uncoil/__init__.py", [".git", ".pyc"])
    assert not matches_skip_pattern("README.md", [])

def test_unfurl_directory(sample_directory):
    """
    Test the unfurl_directory generator.
    """
    skip_list = [".git", ".pyc", "__pycache__", ".venv", "LICENSE"]
    files = list(unfurl_directory(sample_directory, skip_list))
    
    expected_files = [
        str(sample_directory / "README.md"),
        str(sample_directory / "pyproject.toml"),
        str(sample_directory / "src/uncoil/__init__.py"),
        str(sample_directory / "src/uncoil/__main__.py"),
        str(sample_directory / "tests/__init__.py"),
        str(sample_directory / "tests/test_main.py"),
        str(sample_directory / "examples/uncoil.txt")
    ]
    
    assert sorted(files) == sorted(expected_files)

def test_print_file_contents(sample_directory, capsys):
    """
    Test the print_file_contents function.
    """

    console = mock.Mock()
    
    file_path = sample_directory / "README.md"
    print_file_contents(str(file_path), console, SOFT_IGNORE_PATTERNS)
    
    # Assert that console.print was called with the correct content
    console.print.assert_any_call(f"==> {file_path} <==")
    console.print.assert_any_call("# Sample README", markup=False)
    console.print.assert_any_call("\n")

def test_main_with_tags(sample_directory, tmp_path):
    """
    Integration test: Run the main function with tags and verify the output file.
    """
    output_file = tmp_path / "output_with_tags.txt"
    args = [
        "uncoil",
        "-d", str(sample_directory),
        "-o", str(output_file),
        "-t", "fish",
        "-x", ".git,.gitignore,__pycache__,.venv,LICENSE"
    ]
    
    with mock.patch.object(sys, 'argv', args):
        main()
    
    # Read the output file and verify contents
    content = output_file.read_text()
    
    assert content.startswith("<fish>\n")
    assert content.endswith("</fish>\n")
    assert "Directory Structure: " in content
    assert "==> " in content  # Ensures that file contents are included

def test_main_without_tags(sample_directory, tmp_path):
    """
    Integration test: Run the main function without tags and verify the output file.
    """
    output_file = tmp_path / "output_without_tags.txt"
    args = [
        "uncoil",
        "-d", str(sample_directory),
        "-o", str(output_file),
        "-t", "none",
        "-x", ".git,.gitignore,__pycache__,.venv,LICENSE,.pytest_cache"
    ]
    
    with mock.patch.object(sys, 'argv', args):
        main()
    
    # Read the output file and verify contents
    content = output_file.read_text()
    
    assert not content.startswith("<")
    assert not content.endswith(">\n")
    assert "Directory Structure: " in content
    assert "==> " in content  # Ensure that file contents are included

def test_main_default_tags(sample_directory, tmp_path):
    """
    Integration test: Run the main function without specifying the tag to use the default 'codebase'.
    """
    output_file = tmp_path / "output_default_tags.txt"
    args = [
        "uncoil",
        "-d", str(sample_directory),
        "-o", str(output_file),
        "-x", ".git,.gitignore,__pycache__,.venv,LICENSE"
    ]
    
    with mock.patch.object(sys, 'argv', args):
        main()
    
    # Read the output file and verify contents
    content = output_file.read_text()
    
    assert content.startswith("<codebase>\n")
    assert content.endswith("</codebase>\n")
    assert "Directory Structure: " in content
    assert "==> " in content  # Ensure that file contents are included

def test_main_missing_required_argument(tmp_path, capsys):
    """
    Integration test: Run the main function without the required '-d' argument and verify it exits with an error.
    """
    output_file = tmp_path / "output_error.txt"
    args = [
        "uncoil",
        "-o", str(output_file),
        "-t", "fish",
        "-x", ".git,.gitignore,__pycache__,.venv,LICENSE"
    ]
    
    with mock.patch.object(sys, 'argv', args):
        with pytest.raises(SystemExit):
            main()
    
    # Capture the stderr output
    captured = capsys.readouterr()
    assert "error: the following arguments are required: -d/--directory" in captured.err

def test_hard_ignore_defaults_actually_skip(tmp_path):
    # set up a sample project
    # ├── kept.txt
    # └── .pytest_cache/foo.txt
    kept = tmp_path / "kept.txt"
    kept.write_text("keep me")
    bad_dir = tmp_path / ".pytest_cache"
    bad_dir.mkdir()
    ignored = bad_dir / "foo.txt"
    ignored.write_text("you should not see me")

    # The unfurl directory should never yield anything under .pytest_cache
    files = list(unfurl_directory(str(tmp_path), HARD_IGNORE_PATTERNS))
    assert str(ignored) not in files
    assert str(kept) in files

    # Tree should never mention .pytest_cache but should show kept.txt
    tree = create_tree(str(tmp_path), HARD_IGNORE_PATTERNS)

    buf = StringIO()
    console = Console(file=buf, width=80)
    console.print(tree)
    tree_output = buf.getvalue()

    assert ".pytest_cache" not in tree_output
    assert "kept.txt" in tree_output

def test_soft_ignore_produces_stub_not_content(tmp_path):
    # fake binary file matching soft ignore pattern
    img = tmp_path / "pic.JPG"
    img.write_text("THIS_IS_BINARY_DATA")

    # Simulate printing
    console = mock.Mock()

    # Double-check helper
    assert is_soft_ignored(str(img), SOFT_IGNORE_PATTERNS)

    # call the routine
    print_file_contents(str(img), console, SOFT_IGNORE_PATTERNS)

    # It always prints the header
    console.print.assert_any_call(f"==> {str(img)} <==")

    # It prints exactly the stub, not the real contents
    console.print.assert_any_call("[contents ignored]\n", markup=False)

    # It does NOT print the binary payload anywhere
    all_args = [call.args[0] for call in console.print.call_args_list]
    assert "THIS_IS_BINARY_DATA" not in all_args