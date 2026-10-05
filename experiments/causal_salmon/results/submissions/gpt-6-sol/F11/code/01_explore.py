import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "upload/data(20261004-071413).csv"
OUT = ROOT / "submission/results/01_explore.json"

df = pd.read_csv(DATA)
assert list(df.columns) == ["x", "y", "z"]
assert len(df) == 2000 and not df.isna().any().any()
assert set(df.x) == {0, 1}
df["bin"] = pd.cut(df.y, bins=np.arange(0, 101, 5), right=False)
by_bin = df.groupby("bin", observed=False).agg(n=("x", "size"), treated=("x", "sum"), mean_y=("y", "mean"), mean_z=("z", "mean"))
by_bin["p_treated"] = by_bin.treated / by_bin.n
by_bin["treated_z"] = df[df.x == 1].groupby("bin", observed=False).z.mean()
by_bin["control_z"] = df[df.x == 0].groupby("bin", observed=False).z.mean()
by_bin.index = by_bin.index.astype(str)
result = {
    "n": len(df),
    "missing": df.isna().sum().to_dict(),
    "treatment_counts": df.x.value_counts().sort_index().to_dict(),
    "overall": df.groupby("x").agg(n=("z", "size"), mean_y=("y", "mean"), mean_z=("z", "mean"), sd_z=("z", "std")).round(6).to_dict(orient="index"),
    "y_range": {str(x): [float(g.y.min()), float(g.y.max())] for x, g in df.groupby("x")},
    "score_bins": by_bin.round(6).replace({np.nan: None}).reset_index().to_dict(orient="records"),
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)}; n={len(df)}, treated={int(df.x.sum())}")
