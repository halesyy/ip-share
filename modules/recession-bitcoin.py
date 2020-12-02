from packer import Packer
from fdates import parse

P = Packer()

P.dataset(1, {
    "url":              "https://www.newyorkfed.org/medialibrary/media/research/capital_markets/allmonth.xls",
    "name":             "Predicted Recession",
    "index":            "Date",
    "subsets":          ["Rec_prob"],
    "scrape_every":     "1 day"
})
# P.sma(1, "Rec_prob", period=5)

P.dataset(2, {
    "url":              "btcusd=x.yfi",
    "range":            "daily",
    "name":             "BTCUSD",
    "index":            "date",
    "subsets":          ["close"],
    "scrape_every":     "1 day"
})
# P.sma(2, "close", period=20)
# P.percentages(2, "close")

P.minimize([1, 2], normalize=True)

# our "callables" for date parsing our datasets

def nyfed_dp(input):
    s = str(input).split(":")[0].split("T")[0]
    return parse("year-month-day", s, normalize=True)

def yahoofin_dp(input):
    return parse("year-month-day", str(input), normalize=True)

P.parse_indexes_as_date([
    [1, nyfed_dp],
    [2, yahoofin_dp],
])

# Meta-creators
mid = P.index([1], by=2)
mid = P.clean(mid)

P.meta_line_chart("./../bridges/recession_probability_bitcoin.bridge.json", {
    "use": mid,
    "bottom": 0,
    "left": [1],
    "right": [2],
    "names": ["string:Date", "number:Bitcoin", "number:Recession Probability"]
})
