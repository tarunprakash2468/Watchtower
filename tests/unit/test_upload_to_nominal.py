import pandas as pd
from unittest.mock import Mock
from core import import_udl_to_nominal as mod
from pathlib import Path

def test_upload_to_nominal(tmp_path: Path):
    df = pd.DataFrame([{
        "timestamp": "2025-07-03T18:30:00.000000Z",
        "pos.x": 1, "pos.y": 2, "pos.z": 3,
        "vel.x": 4, "vel.y": 5, "vel.z": 6
    }])
    mock_client = Mock()
    mock_dataset = Mock()
    mock_asset = Mock()

    mock_client.create_asset.return_value = mock_asset
    mock_client.create_dataset.return_value = mock_dataset
    mock_asset.add_dataset.return_value = None
    mock_dataset.add_tabular_data.return_value = None
    mock_client.create_run.return_value = None

    mod.upload_to_nominal(mock_client, "TestSat", "25544", "2025-07-03T00:00:00.000000Z", "2025-07-03T01:00:00.000000Z", df)

    mock_client.create_asset.assert_called_once()
    mock_client.create_dataset.assert_called_once()
    mock_client.create_run.assert_called_once()
