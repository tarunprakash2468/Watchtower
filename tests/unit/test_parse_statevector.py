import pandas as pd
from core import import_udl_to_nominal as mod
from typing import List, Dict, Any

def test_parse_statevector_valid():
    data: List[Dict[str, Any]] = [{
        "epoch": "2025-07-03T18:30:00.000000Z",
        "xpos": 1, "ypos": 2, "zpos": 3,
        "xvel": 4, "yvel": 5, "zvel": 6
    }]
    df = mod.parse_statevector(data)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "pos.x" in df.columns

def test_parse_statevector_missing_keys():
    data = [{"epoch": "2025-07-03T18:30:00.000000Z"}]
    df = mod.parse_statevector(data)
    assert df.empty
