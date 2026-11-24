"""Assembles outputs/report_data.json + model coefficients into index.html (run from repo root)."""
import json, sys
sys.path.insert(0, "src")
import pandas as pd
from postlens import fit_model, THEMES, THEME_LABELS

df = pd.read_parquet("outputs/scored.parquet")
ts = df[df.platform == "Truth Social"]
m, _ = fit_model(ts, "Truth Social 2022-26")
R = json.load(open("outputs/report_data.json"))
R["checker"] = {"coef": {k.replace("[T.True]", ""): float(v) for k, v in m.params.items()},
                "themes": THEMES, "labels": THEME_LABELS, "mean_pred": float(m.fittedvalues.mean())}
R["timeline"] = [{"p": "W" if r["platform"] == "Twitter" else "S", "m": r["month"], "n": r["posts"], "l": r["med_likes"]}
                 for r in R["timeline"]]
R["compare"] = json.load(open("outputs/compare.json"))
R["approval"] = {  # Pew Research Center, approval among Trump's 2024 validated voters
    "dates": ["Feb 2025", "Apr 2025", "Jun 2025", "Sep 2025", "Jan 2026", "Apr 2026", "Jul 2026", "Oct 2026"],
    "All Trump 2024 voters": [95, 89, 88, 87, 83, 78, 75, 67], "Hispanic": [93, None, 83, 81, 75, 66, 65, 57],
    "Ages 19-34": [92, 81, 80, 76, 73, 57, 64, 49], "Ages 65+": [96, 91, 92, 90, 86, 88, 80, 76]}
for k in ["top_truth", "top_tw"]:
    R[k] = R[k][:6]
R.pop("bottom_truth", None)
html = open("src/report_template.html").read()
open("index.html", "w").write(html.replace("/*DATA*/", json.dumps(R, separators=(",", ":"), default=float).replace("</", "<\\/")))
print("index.html written")
