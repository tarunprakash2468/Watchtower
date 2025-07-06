import os
from unittest.mock import patch, MagicMock
from core.import_udl_to_nominal import main

@patch.dict(os.environ, {"basicAuth": "x", "nom_key": "y", "n2yo_key": "z"}, clear=True)

@patch("core.import_udl_to_nominal.requests.get")
@patch("core.import_udl_to_nominal.NominalClient.from_token")
@patch("core.import_udl_to_nominal.input")
@patch("core.import_udl_to_nominal.questionary.select")
def test_main_integration_flow(
    mock_select: MagicMock,
    mock_input: MagicMock,
    mock_from_token: MagicMock,
    mock_requests_get: MagicMock
):
    # --- Simulate CLI Inputs ---
    mock_input.side_effect = [
        "12345",  # satellite number
        "2025-07-05T00:00:00.000000Z",  # start
        "2025-07-05T01:00:00.000000Z",  # end
    ]
    mock_select.return_value.ask.return_value = "Rest API"

    # --- Mock UDL API response ---
    mock_requests_get.side_effect = [
        # First call: UDL
        MagicMock(status_code=200, json=lambda: [
            {
                "epoch": "2025-07-05T00:30:00.000000Z",
                "xpos": 1.0,
                "ypos": 2.0,
                "zpos": 3.0,
                "xvel": 4.0,
                "yvel": 5.0,
                "zvel": 6.0,
            }
        ])  # type: ignore[return-value]
        ,
        # Second call: N2YO
        MagicMock(status_code=200, json=lambda: {
            "info": {"satname": "MockSat"}
        })
    ]

    # --- Mock NominalClient behavior ---
    mock_client = MagicMock()
    mock_asset = MagicMock()
    mock_dataset = MagicMock()

    mock_from_token.return_value = mock_client
    mock_client.create_asset.return_value = mock_asset
    mock_client.create_dataset.return_value = mock_dataset

    # Run the main function (no errors should occur)
    main([])

    # ✅ Check key calls
    mock_client.create_asset.assert_called_once()
    mock_client.create_dataset.assert_called_once()
    mock_dataset.add_tabular_data.assert_called_once()
    mock_asset.add_dataset.assert_called_once()
    mock_client.create_run.assert_called_once()