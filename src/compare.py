"""Style fingerprint: Trump vs senior members of Congress, 2020 (same rules, same year)."""
import json, re, sys
import pandas as pd, numpy as np
sys.path.insert(0, "src")
from postlens import style_features, COMPILED

c = pd.read_parquet("data/congress2020.parquet")
c = c[~c.text.str.startswith("RT @")]
PEOPLE = {  # name: (party, accounts)
    "Nancy Pelosi": ("D", ["SpeakerPelosi", "TeamPelosi"]), "Chuck Schumer": ("D", ["SenSchumer"]),
    "Bernie Sanders": ("D", ["SenSanders", "BernieSanders"]), "Alexandria Ocasio-Cortez": ("D", ["AOC", "RepAOC"]),
    "Elizabeth Warren": ("D", ["SenWarren", "ewarren"]), "Kamala Harris": ("D", ["KamalaHarris", "SenKamalaHarris"]),
    "Mitch McConnell": ("R", ["senatemajldr"]), "Kevin McCarthy": ("R", ["GOPLeader"]),
    "Ted Cruz": ("R", ["tedcruz", "SenTedCruz"]), "Marco Rubio": ("R", ["marcorubio", "SenRubioPress"]),
    "Josh Hawley": ("R", ["HawleyMO", "SenHawleyPress"]), "Jim Jordan": ("R", ["Jim_Jordan"]),
    "Matt Gaetz": ("R", ["RepMattGaetz"]), "Elise Stefanik": ("R", ["EliseStefanik"]),
}
OUT = {
    "R": r"\b(democrats?|dems?\b|biden|pelosi|schumer|radical left|socialis|the left\b|liberals?\b|squad|kamala|harris|antifa|fake news)",
    "D": r"\b(republicans?|gop\b|trump|mcconnell|maga\b|right-wing|barr\b|pence|kavanaugh|fox news)",
}
GRAT = COMPILED["gratitude_unity"]
tw = pd.read_csv("data/tweets.csv"); tw["created"] = pd.to_datetime(tw.date, format="mixed")
tw = tw[(tw.isRetweet == "f") & (tw.created.dt.year == 2020) & ~tw.text.str.startswith("RT @")]

def profile(texts, party):
    s = style_features(texts.reset_index(drop=True))
    return {"posts": len(texts), "exclaim": s.s_exclaim.mean() * 100, "caps": s.s_caps_heavy.mean() * 100,
            "outgroup": texts.str.contains(OUT[party], case=False, regex=True).mean() * 100,
            "link": s.s_has_link.mean() * 100, "gratitude": texts.map(lambda x: bool(GRAT.search(x))).mean() * 100,
            "median_words": float(s.s_words.median())}

rows = [{"name": "Donald Trump", "party": "R", **profile(tw.text, "R")}]
for n, (p, acc) in PEOPLE.items():
    rows.append({"name": n, "party": p, **profile(c[c.screen_name.isin(acc)].text, p)})
res = pd.DataFrame(rows)
print(res.round(1).to_string())
json.dump(res.to_dict("records"), open("outputs/compare.json", "w"), default=float)
