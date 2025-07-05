import os
import pytest
from unittest.mock import patch
from typing import Any
from core import import_udl_to_nominal as mod


@patch.dict(os.environ, {'basicAuth': 'abc', 'nom_key': '123', 'n2yo_key': 'xyz'}, clear=True)
@patch("core.import_udl_to_nominal.load_dotenv")  # prevent actual .env loading
def test_load_env_variables_valid(mock_load_dotenv: Any):
    basic_auth, nom_key, n2yo_key = mod.load_env_variables()
    assert basic_auth == "abc"
    assert nom_key == "123"
    assert n2yo_key == "xyz"


@patch.dict(os.environ, {}, clear=True)
@patch("core.import_udl_to_nominal.load_dotenv")  # prevent actual .env loading
def test_load_env_variables_missing(mock_load_dotenv: Any):
    with pytest.raises(ValueError):
        mod.load_env_variables()