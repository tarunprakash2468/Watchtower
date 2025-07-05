import pytest
import subprocess
import sys
import os

@pytest.mark.skipif(
    not os.getenv("CI"),
    reason="Skip subprocess tests during local runs to avoid executing main()"
)

def test_main_entrypoint_runs():
    script_path = os.path.join("core", "import_udl_to_nominal.py")
    result = subprocess.run(
        [sys.executable, script_path, "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0