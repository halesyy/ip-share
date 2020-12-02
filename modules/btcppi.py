from packer import Packer
from fdates import parse

P = Packer()

P.dataset(1, {
    "url":              "http://bitcoinppi.com/v1.1/global_ppi.csv?from=2011-07-01%2000%3A00&to=2020-10-26%2000%3A00",
    "parse_as":         "csv",
    "name":             "Global PPI Bitcoin",
    "index":            "tick",
    "subsets":          ["global_ppi"],
    "scrape_every":     "1 day",
    "reverse":          True
})
# P.sma(1, "Rec_prob", period=5)

P.dataset(2, {
    "url":              "^VIX.yfi",
    "range":            "daily",
    "name":             "VIX",
    "index":            "date",
    "subsets":          ["close"],
    "scrape_every":     "1 day"
})
# P.sma(2, "close", period=5)

P.minimize([1, 2], normalize=True)

# our "callables" for date parsing our datasets

def nyfed_dp(input):
    s = str(input).split(":")[0].split("T")[0]
    return parse("year-month-day", s, normalize=True)

def yahoofin_dp(input):
    return parse("year-month-day", str(input), normalize=True)

def ppi(input):
    return parse("year-month-day", str(input.split(" ")[0]), normalize=True)

P.parse_indexes_as_date([
    [1, ppi],
    [2, nyfed_dp]
])

# Meta-creators
mid = P.index([2], by=1)
mid = P.clean(mid)

P.meta_line_chart("./../bridges/bitcoin_ppi.bridge.json", {
    "use": mid,
    "bottom": 0,
    "left": [1],
    "right": [2],
    "names": ["string:Date", "number:Bitcoin PPI", "number:VIX"]
})
