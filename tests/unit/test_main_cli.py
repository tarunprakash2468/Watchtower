import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
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

# Secure Messaging API triggers streaming

@patch.dict(os.environ, {"basicAuth": "x", "nom_key": "y", "n2yo_key": "z"}, clear=True)

@patch("core.import_udl_to_nominal.stream_secure_messaging_to_nominal")
@patch("core.import_udl_to_nominal.input", side_effect=["12345", "statevector"])
@patch("core.import_udl_to_nominal.questionary.select")
def test_main_secure_api_stream(mock_select: MagicMock, mock_input: MagicMock, mock_stream: MagicMock):
    mock_select.return_value.ask.return_value = "Secure Messaging API"

    from core.import_udl_to_nominal import main
    main([])

    mock_stream.assert_called_once()
