import pytest
from unittest.mock import patch, Mock, MagicMock
from core import import_udl_to_nominal as mod

@patch("requests.get")
def test_list_topics_success(mock_get: MagicMock):
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = [{"topic": "statevector"}]
    mock_get.return_value = mock_resp
    topics = mod.list_topics("auth")
    assert topics == [{"topic": "statevector"}]

@patch("requests.get")
def test_list_topics_fail(mock_get: MagicMock):
    mock_resp = Mock(status_code=500, text="error")
    mock_get.return_value = mock_resp
    with pytest.raises(RuntimeError):
        mod.list_topics("auth")

@patch("requests.get")
def test_get_messages_success(mock_get: MagicMock):
    mock_resp = Mock(status_code=200)
    mock_resp.headers = {"KAFKA_NEXT_OFFSET": "5"}
    mock_resp.json.return_value = [
        {"epoch": "2025-07-05T00:00:00.000000Z", "xpos": 1, "ypos": 2, "zpos": 3, "xvel": 4, "yvel": 5, "zvel": 6}
    ]
    mock_get.return_value = mock_resp
    msgs, next_off = mod.get_messages("auth", "statevector", 1)
    assert isinstance(msgs, list)
    assert next_off == 5

@patch("requests.get")
def test_get_messages_error(mock_get: MagicMock):
    mock_resp = Mock(status_code=500, text="bad")
    mock_get.return_value = mock_resp
    with pytest.raises(RuntimeError):
        mod.get_messages("auth", "statevector", 1)
