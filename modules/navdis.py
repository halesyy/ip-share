from packer import Packer
from fdates import parse

P = Packer()

P.dataset(1, {
    "url":              "https://www.betashares.com.au/files/nav/NDQ_History.csv",
    "parse_as":         "csv",
    "name":             "NAV History",
    "index":            "Date",
    "subsets":          ["NAV"],
    "scrape_every":     "1 day"
})

# toppling is the act of:
# 1. store index [0] of list as x
# 2. prepend x to list
# 3. pop last value off list
P.topple(1, "NAV")

P.dataset(2, {
    "url":              "NDQ.AX.yfi",
    "range":            "daily",
    "name":             "NASDAQ ETF",
    "index":            "date",
    "subsets":          ["close"],
    "scrape_every":     "1 day"
})

P.minimize([1, 2], normalize=True)

# our "callables" for date parsing our datasets

def nyfed_dp(input):
    s = str(input).split(":")[0].split("T")[0]
    return parse("year-month-day", s, normalize=True)

def yahoofin_dp(input):
    return parse("year-month-day", str(input), normalize=True)

P.parse_indexes_as_date([
    [1, yahoofin_dp],
    [2, yahoofin_dp]
])

# Meta-creators
mid = P.index([2], by=1)
mid = P.clean(mid)
mid = P.meta_derive(mid, "dislocation", lambda r: abs(((r[2]-r[1])/r[1])*100))

P.meta_line_chart("./../bridges/nav-dislocation.bridge.json", {
    "use": mid,
    "bottom": 0,
    "left": [3],
    "right": [2],
    "names": ["string:Date", "number:NDQ ETF", "ignore:NDQ MARKET PRICE", "number:Absolute Dislocation"]
})
