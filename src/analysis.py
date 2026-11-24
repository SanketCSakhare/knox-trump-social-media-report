"""Builds the figures/data for the web report from PostLens output."""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "src")
from postlens import THEME_LABELS, fit_model

OUT = "outputs"
df = pd.read_parquet(f"{OUT}/scored.parquet")
eff = pd.read_csv(f"{OUT}/model_effects.csv", index_col=0)
R = {}

# 1. Timeline: monthly volume and median likes per platform (originals only)
m = df.groupby(["platform", df.created.dt.to_period("M").astype(str)]).agg(
    posts=("likes", "size"), med_likes=("likes", "median")).reset_index()
R["timeline"] = m.rename(columns={"created": "month"}).to_dict("records")

# 2. Theme volume share vs effect (Truth Social + Twitter political era)
pol = df[(df.platform == "Truth Social") | (df.created >= "2015-06-16")]
rows = []
for plat, g in pol.groupby("platform"):
    lab = "Truth Social 2022-26" if plat == "Truth Social" else "Twitter 2015-21"
    for k, name in THEME_LABELS.items():
        c = f"t_{k}"
        e = eff[(eff.model == lab)].loc[c] if c in eff[eff.model == lab].index else None
        rows.append({"platform": plat, "theme": k, "label": name, "share": float(g[c].mean() * 100),
                     "median_lift": float(g.loc[g[c], "lift"].median()),
                     "effect": float(e.pct_effect), "lo": float((np.exp(e.lo) - 1) * 100),
                     "hi": float((np.exp(e.hi) - 1) * 100), "p": float(e.p), "n": int(g[c].sum())})
R["themes"] = rows

# 3. Style effects
style_names = {"s_exclaim": "Uses an exclamation mark", "s_caps_heavy": "Mostly CAPITAL LETTERS",
               "s_short": "Very short (15 words or fewer)", "s_long": "Long (over 60 words)",
               "s_question": "Asks a question", "s_has_link": "Contains a link",
               "s_link_only": "Just a link, no comment", "s_quote_other": "Quotes someone else (pundit/fan)",
               "media_only": "Video/image with no text", "night": "Posted 10pm to 6am"}
R["style"] = [{"key": k, "label": v, "model": r.model, "effect": float(r.pct_effect),
               "lo": float((np.exp(r.lo) - 1) * 100), "hi": float((np.exp(r.hi) - 1) * 100), "p": float(r.p),
               "n": int(r.n_with)} for k, v in style_names.items() for _, r in eff[eff.index == k].iterrows()]

# 4. Second term check: refit Truth model on 2025-26 only (is the pattern stable?)
ts = df[df.platform == "Truth Social"]
_, r25 = fit_model(ts[ts.created >= "2025-01-20"], "Truth 2nd term")
_, r22 = fit_model(ts[ts.created < "2025-01-20"], "Truth 2022-24")
both = r22[["pct_effect", "p"]].join(r25[["pct_effect", "p", "n_with"]], lsuffix="_2224", rsuffix="_2526")
R["stability"] = both.reset_index().rename(columns={"index": "feature"}).to_dict("records")
both.to_csv(f"{OUT}/stability.csv")

# 5. Cross-check with the dataset's own (provider) rhetorical_device labels
rd = ts.copy(); rd["rd"] = rd.rhetorical_device.str.split("|").str[0]
rdg = rd.groupby("rd").agg(n=("lift", "size"), median_lift=("lift", "median")).query("n>=200").sort_values("median_lift")
R["rhetoric"] = rdg.reset_index().to_dict("records")
tp = rd.copy(); tp["tp"] = tp.topic.str.split("|").str[0]
tpg = tp.groupby("tp").agg(n=("lift", "size"), median_lift=("lift", "median")).query("n>=200").sort_values("median_lift")
R["provider_topic"] = tpg.reset_index().to_dict("records")

# 6. Volume dilution: posts per day vs median lift that day (Truth Social)
day = ts.groupby(ts.created.dt.date).agg(n=("lift", "size"), lift=("lift", "median"))
bins = pd.cut(day.n, [0, 5, 10, 20, 40, 400], labels=["1-5", "6-10", "11-20", "21-40", "41+"])
R["volume"] = day.groupby(bins, observed=True).agg(days=("n", "size"), median_lift=("lift", "median")).reset_index().astype({"n": str}).to_dict("records")
tday = df[(df.platform == "Twitter") & (df.created >= "2015-06-16")]
tday = tday.groupby(tday.created.dt.date).agg(n=("lift", "size"), lift=("lift", "median"))
tb = pd.cut(tday.n, [0, 5, 10, 20, 40, 400], labels=["1-5", "6-10", "11-20", "21-40", "41+"])
R["volume_tw"] = tday.groupby(tb, observed=True).agg(days=("n", "size"), median_lift=("lift", "median")).reset_index().astype({"n": str}).to_dict("records")

# 7. Top and bottom posts by lift (with enough baseline), short text only
def examples(g, asc, n=8):
    g = g[(g.text.str.len().between(15, 400)) & ~g.s_link_only]
    g = g.sort_values("lift", ascending=asc).head(n)
    return [{"date": str(r.created.date()), "text": r.text[:280], "lift": round(float(r.lift), 1),
             "likes": int(r.likes)} for r in g.itertuples()]
R["top_truth"] = examples(ts, False); R["top_tw"] = examples(df[(df.platform == "Twitter") & (df.created >= "2015-06-16")], False)
R["bottom_truth"] = examples(ts[ts.likes > 0], True)

# 8. Hour of day (ET)
h = ts.groupby(ts.created.dt.hour).agg(n=("lift", "size"), lift=("lift", "median"))
R["hours"] = h.reset_index().rename(columns={"created": "hour"}).to_dict("records")

# 9. Model coefficients for the in-browser Post Checker (Truth Social model)
coef = eff[eff.model == "Truth Social 2022-26"][["coef"]].to_dict()["coef"]
R["checker"] = {"coef": coef, "themes": {k: v for k, v in __import__("postlens").THEMES.items()}}

# 10. Flagged / deleted tweets
tw = df[(df.platform == "Twitter") & (df.created >= "2020-01-01")]
R["deleted"] = tw.groupby("isDeleted").lift.median().to_dict()

# Headline numbers
R["n"] = json.load(open(f"{OUT}/stats.json"))
R["n"]["all_posts"] = 56571 + 32754
json.dump(R, open(f"{OUT}/report_data.json", "w"), default=float)
for k in ["rhetoric", "provider_topic", "volume", "volume_tw", "hours", "deleted"]:
    print(k, pd.DataFrame(R[k]).round(2).to_string() if isinstance(R[k], list) else R[k])
print(both.round(1).to_string())
for k in ["top_truth", "top_tw", "bottom_truth"]:
    print(k); [print(" ", e["date"], e["lift"], e["text"][:120].replace("\n", " ")) for e in R[k]]
