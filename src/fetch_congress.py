"""Download every third day of 2020 from the public congresstweets archive into data/congress2020.parquet."""
import datetime as dt, json, urllib.request
import pandas as pd

BASE = "https://raw.githubusercontent.com/alexlitel/congresstweets/master/data/{}.json"
rows = []
day = dt.date(2020, 1, 2)
while day.year == 2020:
    with urllib.request.urlopen(BASE.format(day.isoformat()), timeout=60) as r:
        rows += json.load(r)
    day += dt.timedelta(days=3)
pd.DataFrame(rows).to_parquet("data/congress2020.parquet")
print(len(rows), "posts saved")
