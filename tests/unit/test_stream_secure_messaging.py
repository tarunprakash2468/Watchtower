from unittest.mock import MagicMock, patch
from core import import_udl_to_nominal as mod


def _fake_response(text=None, json_data=None, headers=None):
    resp = MagicMock()
    if text is not None:
        resp.text = text
    if json_data is not None:
        resp.json.return_value = json_data
    resp.headers = headers or {}
    resp.raise_for_status.return_value = None
    return resp


@patch("core.import_udl_to_nominal.time.sleep")
@patch("core.import_udl_to_nominal.requests.Session")
def test_stream_secure_messaging(mock_session_cls, mock_sleep):
    client = MagicMock()
    dataset = MagicMock()
    asset = MagicMock()
    stream = MagicMock()
    dataset.get_write_stream.return_value.__enter__.return_value = stream
    client.create_dataset.return_value = dataset
    client.create_asset.return_value = asset

    session = MagicMock()
    mock_session_cls.return_value = session
    session.get.side_effect = [
        _fake_response(text="5"),
        _fake_response(json_data=[{
            "epoch": "2025-01-01T00:00:00Z",
            "xpos": 1,
            "ypos": 2,
            "zpos": 3,
            "xvel": 4,
            "yvel": 5,
            "zvel": 6
        }], headers={"KAFKA_NEXT_OFFSET": "6"})
    ]

    mod.stream_secure_messaging_to_nominal(client, "auth", "statevector", "sat", max_messages=1, sample_period=0)

    dataset.get_write_stream.assert_called_once()
    stream.enqueue.assert_any_call("pos.x", "2025-01-01T00:00:00Z", 1)
    asset.add_dataset.assert_called_once()
