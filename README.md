# What drives engagement on Donald Trump's social media (2009 to 2026)

Case study for Knox, written for the Atlantic Data Institute brief.

**Live report:** https://sanketcsakhare.github.io/knox-trump-social-media-report/

## Main findings

- Emotional style lifts his posts. An exclamation mark adds about 18% more likes on Truth Social, and mostly capital letters add about 17%.
- Party work does badly. Endorsing other candidates gets 40% fewer likes than his normal, and links get 22% fewer.
- Some content only works with his base. Election fraud claims beat his normal by 12% on Truth Social but did 10% worse on Twitter.
- He gets more per post on quiet days: 1.49x his normal with 1 to 5 posts a day, against 0.74x with 41 or more.
- Engagement on Truth Social held steady in 2026 while approval among his own 2024 voters fell from 95% to 67% (Pew). Likes measure loyalty, not persuasion.

## The tool: PostLens

`src/postlens.py` does the core work:

1. Cleans and merges the Twitter archive (2009 to 2021) and the Truth Social archive (2022 to 2026). It rebuilds the repost flag, which is false on every row in the source file.
2. Scores each post as **lift**: its likes divided by the median likes of his own posts in the surrounding 31 days. This makes a 2013 tweet comparable with a 2025 Truth Social post.
3. Tags each post with 16 content themes and 9 style features using readable keyword rules (the `THEMES` dictionary).
4. Fits a regression of log(lift) on all tags at once, separately for each platform.

The report's **Post Checker** runs the same rules and the Truth Social model in the browser, so you can paste a draft post and see its expected lift.

## Repository layout

| Path | What it is |
|---|---|
| `index.html` | The web report (self-contained) |
| `src/postlens.py` | Cleaning, lift scoring, theme tagging, regression |
| `src/analysis.py` | Builds the report figures and the second-term stability check |
| `src/compare.py` | Style comparison with 14 senior members of Congress (2020) |
| `src/fetch_congress.py` | Downloads the congresstweets sample used by `compare.py` |
| `outputs/model_effects.csv` | Effect of every theme and style feature, both platforms |
| `outputs/stability.csv` | Truth Social effects before and after January 2025 |
| `outputs/hand_check_sample.csv` | 240 posts (15 per theme) for checking tag accuracy, drawn before the rule fixes below |
| `src/build_page.py`, `src/report_template.html` | Build `index.html` from the model outputs |

## Run it

The source datasets belong to Knox and are not included. Put them in `data/` as `tweets.csv` and `truth.csv`, then:

```
pip install pandas numpy statsmodels ftfy pyarrow
mkdir -p data outputs
python src/postlens.py data/tweets.csv data/truth.csv outputs
python src/analysis.py
python src/fetch_congress.py && python src/compare.py
python src/build_page.py
```

## Limits

- Likes are not votes, and Truth Social is a small, self-selected audience.
- The results are associations, not causes.
- Keyword tags are approximate. A post that mentions a theme is not always about it.
- 5,292 Truth Social posts with zero engagement were dropped as likely collection errors.

## Rule fixes after review

A full-text review of 240 tagged posts found weak economy, faith, foreign policy and technology tags. The rules were then changed so that "great job" no longer counts as jobs, "Eastern" as Easter, "tax returns" as economy, "God Bless" as faith, "Russia hoax" and "war on…" as foreign policy, or "Elon/Musk" as technology, and endorsement templates no longer count as foreign policy. Both models were refitted. The headline findings did not change.

## Use of AI

AI tools helped write the code, gather outside sources and draft the report. The method note submitted with this case study explains which parts were checked by hand.
