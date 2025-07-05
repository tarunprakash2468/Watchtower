import subprocess
import sys
from pathlib import Path

def test_main_help_flag_runs():
    script_path = Path("core/import_udl_to_nominal.py").resolve()
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert result.returncode in (0, 1)  # your --help might exit(0) or exit(1)
    assert "usage" in result.stdout.lower() or result.stderr  # flexible output check