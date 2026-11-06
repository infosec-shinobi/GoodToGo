import shutil
import subprocess
from pathlib import Path

import pytest


def test_workbook_browser_logic():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for the dependency-free workbook JavaScript tests")
    result = subprocess.run(
        [node, "--test", "tests/js/workbook.test.cjs"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
