# tests/test_main.py

import os
import sys
import pytest
import tempfile
from unittest import mock
from pathlib import Path
from io import StringIO

# Import the main module from the uncoil package
from src.uncoil.__main__ import (
    matches_skip_pattern,
    unfurl_directory,
    create_tree,
    print_file_contents,
    main
)

from rich.tree import Tree

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
    assert matches_skip_pattern("src/uncoil/__init__.py", [".git", ".pyc"]) == False
    assert matches_skip_pattern(".git/config", [".git", ".pyc"]) == True
    assert matches_skip_pattern("src/uncoil/__pycache__/file.pyc", [".git", ".pyc"]) == True
    assert matches_skip_pattern("README.md", []) == False
    assert matches_skip_pattern("README.md", ["README"]) == True

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
    # Capture the console output
    captured_output = StringIO()
    console = mock.Mock()
    
    file_path = sample_directory / "README.md"
    print_file_contents(file_path, console)
    
    # Assert that console.print was called with the correct content
    console.print.assert_any_call(f"==> {file_path} <==")
    console.print.assert_any_call("# Sample README")
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
        with pytest.raises(SystemExit) as exc_info:
            main()
    
    # Capture the stderr output
    captured = capsys.readouterr()
    assert "error: the following arguments are required: -d/--directory" in captured.err
