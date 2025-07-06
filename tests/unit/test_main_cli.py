import subprocess
import sys
from pathlib import Path
import pytest
import os

@pytest.mark.skipif(
    not os.getenv("CI"),
    reason="Skip subprocess tests during local runs to avoid executing main()"
)

def test_main_help_flag_runs():
    script_path = Path("core/import_udl_to_nominal.py").resolve()
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert result.returncode in (0, 1)  # your --help might exit(0) or exit(1)
    assert "usage" in result.stdout.lower() or "usage" in result.stderr.lower()

# Test for Secure Messaging API exit path
from unittest.mock import patch, MagicMock

@patch.dict(os.environ, {"basicAuth": "x", "nom_key": "y", "n2yo_key": "z"}, clear=True)

@patch("builtins.print")
@patch("core.import_udl_to_nominal.sys.exit", side_effect=SystemExit)
@patch("core.import_udl_to_nominal.input", side_effect=["12345", "2025-07-05T00:00:00.000Z", "2025-07-05T01:00:00.000Z"])
@patch("core.import_udl_to_nominal.questionary.select")
def test_main_secure_api_exit(mock_select: MagicMock, mock_input: MagicMock, mock_exit: MagicMock, mock_print: MagicMock):
    mock_select.return_value.ask.return_value = "Secure Messaging API"

    from core.import_udl_to_nominal import main
    with pytest.raises(SystemExit):
        main()

    mock_print.assert_any_call("Secure Messaging API requires access request. Contact UDL support.")
    mock_exit.assert_called_once_with(1)