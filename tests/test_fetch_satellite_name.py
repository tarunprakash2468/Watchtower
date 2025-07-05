from unittest.mock import patch, Mock, MagicMock
from core import import_udl_to_nominal as mod

@patch("requests.get")
def test_fetch_satellite_name(mock_get: MagicMock):
    mock_response = Mock()
    mock_response.json.return_value = {"info": {"satname": "TestSat"}}
    mock_get.return_value = mock_response
    name = mod.fetch_satellite_name("1234", "key")
    assert name == "TestSat"
