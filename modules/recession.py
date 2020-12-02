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
P.sma(1, "Rec_prob", period=5)

P.dataset(2, {
    "url":              "^VIX.yfi",
    "range":            "daily",
    "name":             "VIX",
    "index":            "date",
    "subsets":          ["close"],
    "scrape_every":     "1 day"
})
P.sma(2, "close", period=5)

P.dataset(3, {
    "url":              "^GSPC.yfi",
    "range":            "daily",
    "name":             "NASDAQ",
    "index":            "date",
    "subsets":          ["close"],
    "scrape_every":     "1 day"
})
P.sma(3, "close", period=5)

P.dataset(4, {
    "url":              "^IXIC.yfi",
    "range":            "daily",
    "name":             "NASDAQ",
    "index":            "date",
    "subsets":          ["close"],
    "scrape_every":     "1 day"
})
P.sma(4, "close", period=5)

P.minimize([1, 2, 3, 4], normalize=True)

# our "callables" for date parsing our datasets

def nyfed_dp(input):
    s = str(input).split(":")[0].split("T")[0]
    return parse("year-month-day", s, normalize=True)

def yahoofin_dp(input):
    return parse("year-month-day", str(input), normalize=True)

P.parse_indexes_as_date([
    [1, nyfed_dp],
    [2, yahoofin_dp],
    [3, yahoofin_dp],
    [4, yahoofin_dp]
])

# Meta-creators
mid = P.index([2, 3, 4], by=1)
mid = P.clean(mid)

P.meta_line_chart("./../bridges/recession_probability_vix.bridge.json", {
    "use": mid,
    "bottom": 0,
    "left": [1],
    "right": [2],
    "random": [3, 4],
    "names": ["string:Date", "number:Recession Probability", "number:VIX", "number:S&P", "number:NASDAQ"]
})
