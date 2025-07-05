from unittest.mock import patch
from core import import_udl_to_nominal as mod
from unittest.mock import MagicMock

@patch("core.import_udl_to_nominal.questionary.select")
def test_select_udl_api(mock_select: MagicMock):
    # Simulate user selecting "Rest API"
    mock_select.return_value.ask.return_value = "Rest API"

    result = mod.select_udl_api()

    assert result == "Rest API"
    mock_select.assert_called_once()
    mock_select.return_value.ask.assert_called_once()