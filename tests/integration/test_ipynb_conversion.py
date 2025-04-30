import pytest
from io import StringIO
from rich.console import Console
from uncoil.__main__ import print_file_contents
from pathlib import Path

@pytest.fixture
def fixture_notebook_path():
    return Path(__file__).parent / "test.ipynb"

def test_integration_jupytext_with_real_notebook(fixture_notebook_path):
    console = Console(file=StringIO())
    print_file_contents(str(fixture_notebook_path), console, [])
    output = console.file.getvalue()
    
    # Should go through jupytext and emit the percent markers
    assert "# %%" in output
    assert "fixture works" in output
