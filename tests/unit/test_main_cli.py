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

# Test Secure Messaging API flow

@patch.dict(os.environ, {"basicAuth": "x", "nom_key": "y", "n2yo_key": "z"}, clear=True)
@patch("core.import_udl_to_nominal.upload_to_nominal")
@patch("core.import_udl_to_nominal.fetch_satellite_name", return_value="TestSat")
@patch("core.import_udl_to_nominal.get_messages")
@patch("core.import_udl_to_nominal.get_latest_offset", return_value=10)
@patch("core.import_udl_to_nominal.list_topics", return_value=[{"topic": "statevector"}])
@patch("core.import_udl_to_nominal.NominalClient.from_token")
@patch("core.import_udl_to_nominal.input", side_effect=[
    "12345",  # sat number
    "2025-07-05T00:00:00.000000Z",  # start
    "2025-07-05T01:00:00.000000Z",  # end
    "statevector",  # topic
])
@patch("core.import_udl_to_nominal.questionary.select")
def test_main_secure_api_flow(
    mock_select: MagicMock,
    mock_input: MagicMock,
    mock_from_token: MagicMock,
    mock_list_topics: MagicMock,
    mock_get_latest_offset: MagicMock,
    mock_get_messages: MagicMock,
    mock_fetch_name: MagicMock,
    mock_upload: MagicMock,
):
    mock_select.return_value.ask.return_value = "Secure Messaging API"
    mock_get_messages.return_value = ([{
        "epoch": "2025-07-05T00:00:00.000000Z",
        "xpos": 1,
        "ypos": 2,
        "zpos": 3,
        "xvel": 4,
        "yvel": 5,
        "zvel": 6,
    }], 11)

    from core.import_udl_to_nominal import main
    main([])

    mock_list_topics.assert_called_once()
    mock_get_latest_offset.assert_called_once_with("x", "statevector")
    mock_get_messages.assert_called_once_with("x", "statevector", 10)
    mock_upload.assert_called_once()
