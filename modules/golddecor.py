from packer import Packer
from fdates import parse

P = Packer()

P.dataset(1, {
    "url":              "https://www.gold.org/download/file/8369/Prices.xlsx",

    "requires_login":   True,
    "sheet":            "Daily_Indexed",
    "skip":             8,

    "headers": {
        "cookie": "__cfduid=d47f5383bd31f1b855bdff582f54887f71603764762; wgc=78e0f8ca0ceb20ba0a6e496c0f2a4b29; SSESSff3c9c8487bbd28d0242841ec9b7eb17=vm9S5olxCU7ZPZAlLm9wqqZEV9ny4w7dKgKLs6CGOYY; AWSALB=ENgx+z22qC91HDdO2QwVS9268b+DChn/hLUBCkdXdOnXfCp7C5knjKEkI2PgqnJu+PhdqnYlUBRNempF4M6dfD/ZssxTZ/J/I0bT3Y7QCxt1Y+PQzop6kmC4IJyI; AWSALBCORS=ENgx+z22qC91HDdO2QwVS9268b+DChn/hLUBCkdXdOnXfCp7C5knjKEkI2PgqnJu+PhdqnYlUBRNempF4M6dfD/ZssxTZ/J/I0bT3Y7QCxt1Y+PQzop6kmC4IJyI",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "upgrade-insecure-requests": "1",
    },

    "name":             "GOLD",
    "index":            "Name",
    "subsets":          ["US dollar"],
    "scrape_every":     "1 day"
})

# toppling is the act of:
# 1. store index [0] of list as x
# 2. prepend x to list
# 3. pop last value off list
# P.topple(1, "NAV")

P.dataset(2, {
    "url":              "GOLD.yfi",
    "range":            "daily",
    "name":             "NYSE:GOLD",
    "index":            "date",
    "subsets":          ["close"],
    "scrape_every":     "1 day"
})

P.dataset(3, {
    "url": "DX-Y.NYB.yfi",
    "range": "daily",
    "name": "Dollar Index",
    "index": "date",
    "subsets": ["close"],
    "scrape_every": "1 day"
})

P.minimize([1, 2, 3], normalize=True)

# our "callables" for date parsing our datasets

def gold(input):
    # print(input)
    s = str(input).split("T")[0]
    return parse("year-month-day", s, normalize=True)

def yahoofin_dp(input):
    # print(input)
    return parse("year-month-day", str(input), normalize=True)

P.parse_indexes_as_date([
    [1, gold],
    [2, yahoofin_dp],
    [3, yahoofin_dp]
])

# Meta-creators
mid = P.index([1, 3], by=2)
mid = P.clean(mid)
# mid = P.meta_derive(mid, "dislocation", lambda r: abs(((r[2]-r[1])/r[1])*100))

P.meta_line_chart("./../bridges/gold.bridge.json", {
    "use": mid,
    "bottom": 0,
    "left": [1],
    "right": [2],
    "random": [3],
    "names": ["string:Date", "number:NYSE-GOLD", "number:Gold Spot", "number:Dollar Index"]
})
