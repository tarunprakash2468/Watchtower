import pytest
from unittest.mock import patch, Mock, MagicMock
from core import import_udl_to_nominal as mod

@patch("requests.get")
def test_fetch_udl_data_success(mock_get: MagicMock):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"epoch": "value"}]
    mock_get.return_value = mock_response
    data = mod.fetch_udl_data("url", "auth")
    assert isinstance(data, list)

@patch("requests.get")
def test_fetch_udl_data_fail(mock_get: MagicMock):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "error"
    mock_get.return_value = mock_response
    with pytest.raises(RuntimeError):
        mod.fetch_udl_data("url", "auth")
