import pandas as pd
import numpy as np
from src.pipeline import engineer_features

def test_engineer_features_shapes():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=5, freq="D"),
        "open":[1,2,3,4,5],
        "high":[1,2,3,4,5],
        "low":[1,2,3,4,5],
        "close":[1,2,3,4,5],
        "adj_close":[1.0,1.1,1.21,1.331,1.4641],
        "volume":[10,11,12,13,14],
    })
    out = engineer_features(df)
    assert {"daily_return","ma_20","ma_50","vol_20"}.issubset(out.columns)
    # first daily_return can be NaN; later ones numeric
    assert np.isnan(out.loc[0,"daily_return"])
    assert out["ma_20"].iloc[-1] > 0
