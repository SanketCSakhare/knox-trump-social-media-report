"""
PostLens: a transparent toolkit for scoring political social media posts.

What it does
1. Cleans and merges the Twitter (2009-2021) and Truth Social (2022-2026) archives.
2. Scores every original post against the account's own baseline at the time
   ("lift"), so a 2016 tweet and a 2025 Truth can be compared fairly.
3. Tags each post with content themes and style features using a rule book of
   keyword patterns (THEMES below). Rules are readable and auditable, so any
   tag can be checked by hand.
4. Fits a regression of log(lift) on themes + style, so each feature's effect is
   measured holding the others constant.
5. Exports JSON for the web report and the in-browser Post Checker.

Usage:  python3 postlens.py <tweets.csv> <truth.csv> <out_dir>
"""
import json, re, sys
import numpy as np
import pandas as pd
import ftfy
import statsmodels.formula.api as smf

# ---------------------------------------------------------------- rule book
# Each theme = list of regex patterns (case-insensitive, word boundaries).
THEMES = {
    "economy_prices": [r"inflation", r"prices?", r"gas\b", r"groceries", r"stock market", r"jobs?\b",
                       r"economy", r"tax(es)?\b", r"tariffs?", r"wages?", r"interest rates?", r"\bfed\b",
                       r"powell", r"affordab", r"egg prices", r"401k", r"dow\b", r"s&p"],
    "immigration_border": [r"border", r"illegal (alien|immigra|migrant)", r"migrants?", r"deport", r"\bice\b",
                           r"\bwall\b", r"invasion", r"sanctuary", r"asylum", r"cartel"],
    "crime_law_order": [r"crime rates?", r"violent crime", r"crime is", r"criminals? (aliens|migrants|gangs)", r"police", r"law and order", r"law & order", r"murder",
                        r"violent", r"fentanyl", r"\bgangs?\b", r"\bms-13\b", r"national guard"],
    "faith_values": [r"\bgod\b", r"christian", r"church", r"pray(er|ers|ing)?", r"bible", r"faith",
                     r"religio", r"christmas", r"easter", r"abortion", r"pro.?life", r"\bjesus\b"],
    "legal_persecution": [r"witch ?hunt", r"indict", r"\bdoj\b", r"\bfbi\b", r"jack smith", r"bragg",
                          r"letitia james", r"engoron", r"\bjudge\b", r"prosecut", r"weaponiz", r"mar-a-lago raid",
                          r"lawfare", r"\bhoax\b", r"e\.? jean carroll", r"\btrial\b", r"persecut", r"immunity"],
    "election_fraud": [r"rigged", r"fraud", r"stolen election", r"cheat", r"ballot", r"voter id",
                       r"mail-in", r"dominion", r"election interference", r"2000 mules"],
    "media_attack": [r"fake news", r"\bcnn\b", r"msdnc", r"msnbc", r"new york times", r"failing .?times",
                     r"washington post", r"\bnbc\b", r"\babc\b", r"\bcbs\b", r"enemy of the people",
                     r"lamestream", r"60 minutes", r"corrupt media"],
    "attack_opponent": [r"crooked", r"sleepy joe", r"crooked joe", r"kamala", r"\bbiden\b", r"pelosi",
                        r"schumer", r"\bobama\b", r"hillary", r"radical left", r"democrats?\b", r"newscum",
                        r"newsom", r"\baoc\b", r"marxist", r"communist", r"\bdesanctimonious\b", r"desantis",
                        r"\bhaley\b", r"birdbrain", r"lunatic", r"loser", r"\brino\b"],
    "endorsement": [r"complete and total endorsement", r"has my complete", r"endorse", r"strongly supported",
                    r"\bvote for\b", r"running for", r"congressional district", r"re-?election", r"state (senate|house)",
                    r"champion for", r"(warrior|fighter|advocate|representative) for", r"america first (patriot|warrior|fighter|champion)",
                    r"will (fight|work) (hard )?(to|for)", r"doing a (truly )?(fantastic|great|tremendous) job representing",
                    r"(congressman|congresswoman|senator|governor|attorney general|state representative) [A-Z][a-z]+ [A-Z][a-z]+ (is|has|will)"],
    "foreign_peace": [r"china", r"russia", r"ukraine", r"putin", r"\bxi\b", r"iran", r"israel", r"gaza",
                      r"\bnato\b", r"north korea", r"world war", r"\bwar\b", r"\bpeace\b", r"ceasefire", r"hamas"],
    "military_patriotic": [r"veterans?", r"military", r"soldiers?", r"troops", r"\barmy\b", r"\bnavy\b",
                           r"memorial day", r"independence day", r"4th of july"],
    "health_maha": [r"\bmaha\b", r"\brfk\b", r"robert f\.? kennedy", r"bobby kennedy", r"vaccin", r"autism", r"food dye", r"chronic disease",
                    r"obamacare", r"healthcare", r"drug prices", r"covid", r"pharma"],
    "tech_crypto": [r"crypto", r"bitcoin", r"\bai\b", r"artificial intelligence", r"\belon\b", r"musk",
                    r"tiktok", r"blockchain", r"stablecoin", r"tech\b"],
    "sports_culture": [r"\bufc\b", r"super bowl", r"\bnfl\b", r"\bgolf\b", r"football", r"baseball",
                       r"rogan", r"podcast", r"\bwrestl", r"daytona", r"olympic", r"\bwoke\b", r"transgender",
                       r"women.?s sports"],
    "gratitude_unity": [r"thank you", r"\bthanks\b", r"congratulations", r"rest in peace", r"\brip\b",
                        r"condolences", r"our hearts", r"happy (birthday|thanksgiving|new year|mother|father)",
                        r"god bless", r"merry christmas", r"great honor"],
    "self_promo_win": [r"\bpoll(s|ing)?\b", r"record\b", r"ratings", r"crowd", r"number one", r"#1\b",
                       r"\bbook\b", r"landslide", r"\bwin(ning)?\b", r"winning", r"massive", r"\bmaga\b",
                       r"make america great again"],
}
THEME_LABELS = {
    "economy_prices": "Economy, prices & tariffs", "immigration_border": "Immigration & border",
    "crime_law_order": "Crime & law and order", "faith_values": "Faith & values",
    "legal_persecution": "His legal cases ('witch hunt')", "election_fraud": "Election fraud claims",
    "media_attack": "Attacks on the media", "attack_opponent": "Attacks on named opponents",
    "endorsement": "Endorsing other candidates", "foreign_peace": "Foreign policy, war & peace",
    "military_patriotic": "Military, veterans & patriotism", "health_maha": "Health & MAHA",
    "tech_crypto": "Tech, AI & crypto", "sports_culture": "Sports & culture war",
    "gratitude_unity": "Gratitude, condolence & unity moments", "self_promo_win": "Winning, polls & self-promotion",
}
# every pattern must start at a word boundary (stops "pray" matching "spray", "ice" matching "price")
COMPILED = {k: re.compile(r"\b(?:" + "|".join(v) + ")", re.I) for k, v in THEMES.items()}


ISSUE_THEMES = ["economy_prices", "immigration_border", "crime_law_order", "faith_values",
                "military_patriotic", "health_maha", "tech_crypto", "sports_culture", "self_promo_win"]


def tag_themes(text: pd.Series) -> pd.DataFrame:
    out = pd.DataFrame({f"t_{k}": text.map(lambda x, p=p: bool(p.search(x))) for k, p in COMPILED.items()})
    # Endorsement posts use a template that lists issues ("Secure the Border, Grow the Economy,
    # Support our Military...") -- a hand check showed this polluting the issue themes, so an
    # endorsement post is not also counted as an issue post.
    for k in ISSUE_THEMES:
        out[f"t_{k}"] &= ~out["t_endorsement"]
    return out


def style_features(text: pd.Series) -> pd.DataFrame:
    letters = text.str.count(r"[A-Za-z]").replace(0, np.nan)
    caps = text.str.count(r"[A-Z]")
    words = text.str.split().str.len().fillna(0)
    url_only = text.str.fullmatch(r"\s*(https?://\S+\s*)+", na=False)
    return pd.DataFrame({
        "s_words": words,
        "s_short": (words <= 15) & ~url_only,               # 15 words or fewer
        "s_long": words > 60,
        "s_caps_heavy": (caps / letters).fillna(0) > 0.5,   # mostly CAPITALS
        "s_exclaim": text.str.count("!") >= 1,
        "s_question": text.str.contains(r"\?", na=False),
        "s_has_link": text.str.contains(r"https?://", na=False),
        "s_link_only": url_only,
        "s_quote_other": text.str.contains(r'^\s*["“]|^[A-Z][a-z]+ [A-Z][a-z]+:\s*["“]|^"@', na=False),  # quoting a TV pundit
    })


def load_twitter(path):
    d = pd.read_csv(path)
    d["created"] = pd.to_datetime(d["date"], format="mixed")
    d = d[(d.isRetweet == "f") & ~d.text.str.startswith("RT @")].copy()  # also drop manual "RT @" copies                     # retweets carry 0 likes in this export
    d = d.drop_duplicates(subset=["text", "date"])
    d["platform"] = "Twitter"
    d["likes"] = d["favorites"]; d["shares"] = d["retweets"]; d["replies"] = np.nan
    d["media_only"] = False
    return d[["created", "platform", "text", "likes", "shares", "replies", "media_only", "isDeleted"]]


def load_truth(path):
    t = pd.read_csv(path, low_memory=False)
    t["created"] = pd.to_datetime(t["created_at"], format="mixed", utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    t["text"] = t["text"].fillna("").map(ftfy.fix_text)
    t["is_rt"] = t["text"].str.match(r"^RT[ :@]")          # source flag is_retruth is always False; rebuild it
    t["platform"] = "Truth Social"
    t["likes"] = t["like_count"]; t["shares"] = t["retruth_count"]; t["replies"] = t["reply_count"]
    t["media_only"] = ~t["has_text"]
    t["isDeleted"] = "f"
    zero = (t.like_count == 0) & (t.retruth_count == 0) & (t.reply_count == 0)
    stats = {"truth_raw": len(t), "truth_rt": int(t.is_rt.sum()), "truth_zero": int(zero.sum()),
             "truth_media_only": int((~t.has_text).sum())}
    t = t[~t.is_rt & ~zero].copy()
    keep = ["created", "platform", "text", "likes", "shares", "replies", "media_only", "isDeleted",
            "topic", "rhetorical_device", "toxicity_score", "sentiment_score"]
    return t[keep], stats


def add_lift(df, window_days=31):
    """lift = likes / median likes of the same account's original posts in a centred 31-day window."""
    out = []
    for _, g in df.groupby("platform"):
        g = g.sort_values("created").set_index("created")
        base = g["likes"].rolling(f"{window_days}D", center=True, min_periods=10).median()
        g["baseline"] = base
        out.append(g.reset_index())
    df = pd.concat(out)
    df = df[df.baseline > 0].copy()
    df["lift"] = df.likes / df.baseline
    df["log_lift"] = np.log((df.likes + 1) / (df.baseline + 1))
    return df


def fit_model(df, label):
    feats = [c for c in df.columns if c.startswith("t_")] + \
            ["s_short", "s_long", "s_caps_heavy", "s_exclaim", "s_question", "s_has_link", "s_link_only", "s_quote_other"]
    if "media_only" in df and df.media_only.any():
        feats.append("media_only")
    feats = [f for f in feats if df[f].astype(int).std() > 0]   # drop features with no variation
    X = df[feats].astype(int)
    d = pd.concat([X, df[["log_lift"]], df.created.dt.hour.rename("hour")], axis=1)
    d["night"] = ((d.hour >= 22) | (d.hour < 6)).astype(int)
    formula = "log_lift ~ " + " + ".join(feats + ["night"])
    m = smf.ols(formula, data=d).fit(cov_type="HC3")
    res = pd.DataFrame({"coef": m.params, "lo": m.conf_int()[0], "hi": m.conf_int()[1], "p": m.pvalues})
    res = res.drop("Intercept")
    res.index = res.index.str.replace(r"\[T\.True\]", "", regex=True)
    res["pct_effect"] = (np.exp(res.coef) - 1) * 100      # % change in likes vs the account's baseline
    res["n_with"] = [int(d[f].sum()) for f in res.index]
    res["model"] = label
    return m, res


def main(tw_path, tr_path, out):
    tw = load_twitter(tw_path)
    tr, stats = load_truth(tr_path)
    df = pd.concat([tw, tr], ignore_index=True)
    df["text"] = df["text"].fillna("")
    df = pd.concat([df.reset_index(drop=True), tag_themes(df.text).reset_index(drop=True),
                    style_features(df.text).reset_index(drop=True)], axis=1)
    df = add_lift(df)
    df.to_parquet(f"{out}/scored.parquet")
    # Analysis windows: political Twitter era (from launch of 2016 campaign) and Truth Social
    pol_tw = df[(df.platform == "Twitter") & (df.created >= "2015-06-16")]
    ts = df[df.platform == "Truth Social"]
    m1, r1 = fit_model(pol_tw, "Twitter 2015-21")
    m2, r2 = fit_model(ts, "Truth Social 2022-26")
    res = pd.concat([r1, r2])
    res.to_csv(f"{out}/model_effects.csv")
    stats.update({"twitter_original_scored": len(df[df.platform == "Twitter"]),
                  "twitter_political_era": len(pol_tw), "truth_scored": len(ts),
                  "r2_twitter": m1.rsquared, "r2_truth": m2.rsquared})
    json.dump(stats, open(f"{out}/stats.json", "w"), indent=1, default=float)
    print(json.dumps(stats, indent=1, default=float))
    print(res.sort_values(["model", "pct_effect"]).round(3).to_string())


if __name__ == "__main__":
    main(*sys.argv[1:4])
