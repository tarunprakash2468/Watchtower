import builtins
from datetime import datetime
from unittest.mock import patch, MagicMock
from core import import_udl_to_nominal as mod

@patch.object(builtins, "input", side_effect=[
    "invalid-date",               # Invalid input
    "2025-07-03T18:30:00.000000Z" # Valid input
])
def test_get_valid_date(mock_input: MagicMock):
    result = mod.get_valid_date("test")
    assert isinstance(result, datetime)
    assert result == datetime(2025, 7, 3, 18, 30, 0, 0)