import os
from unittest.mock import patch, MagicMock
from core.import_udl_to_nominal import main

@patch.dict(os.environ, {"basicAuth": "x", "nom_key": "y", "n2yo_key": "z"}, clear=True)
@patch("core.import_udl_to_nominal.upload_to_nominal")
@patch("core.import_udl_to_nominal.fetch_satellite_name", return_value="MockSat")
@patch("core.import_udl_to_nominal.get_messages")
@patch("core.import_udl_to_nominal.get_latest_offset", return_value=5)
@patch("core.import_udl_to_nominal.list_topics", return_value=[{"topic": "statevector"}])
@patch("core.import_udl_to_nominal.NominalClient.from_token")
@patch("core.import_udl_to_nominal.input")
@patch("core.import_udl_to_nominal.questionary.select")
def test_main_secure_messaging_flow(
    mock_select: MagicMock,
    mock_input: MagicMock,
    mock_from_token: MagicMock,
    mock_list_topics: MagicMock,
    mock_get_latest_offset: MagicMock,
    mock_get_messages: MagicMock,
    mock_fetch_name: MagicMock,
    mock_upload: MagicMock,
):
    mock_input.side_effect = [
        "12345",  # satellite number
        "2025-07-05T00:00:00.000000Z",  # start
        "2025-07-05T01:00:00.000000Z",  # end
        "statevector",  # topic
    ]
    mock_select.return_value.ask.return_value = "Secure Messaging API"
    mock_get_messages.return_value = ([{
        "epoch": "2025-07-05T00:00:00.000000Z",
        "xpos": 1,
        "ypos": 2,
        "zpos": 3,
        "xvel": 4,
        "yvel": 5,
        "zvel": 6,
    }], 6)
    main([])
    mock_upload.assert_called_once()
