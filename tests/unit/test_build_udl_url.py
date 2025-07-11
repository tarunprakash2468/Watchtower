import pytest
from core import import_udl_to_nominal as mod

def test_build_udl_url_rest():
    url = mod.build_udl_url("Rest API", "1234", "start", "end")
    assert "statevector" in url

def test_build_udl_url_history_rest():
    url = mod.build_udl_url("History Rest API", "1234", "start", "end")
    assert "statevector" in url

def test_build_udl_url_bulk_data_request():
    url = mod.build_udl_url("Bulk Data Request API", "1234", "start", "end")
    assert "statevector" in url

def test_build_udl_url_invalid():
    with pytest.raises(ValueError):
        mod.build_udl_url("Invalid API", "1234", "start", "end")
