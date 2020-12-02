from packer import Packer
from fdates import parse

P = Packer()

P.d_fred(1, "https://alfred.stlouisfed.org/graph/alfredgraph.csv?bgcolor=%23e1e9f0&chart_type=column&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=alfred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=MRTSSM44511USN,MRTSSM44511USN&scale=left,left&cosd=2001-01-01,2001-01-01&coed=2020-07-01,2020-08-01&line_color=%234572a7,%23aa4643&link_values=false,false&line_style=solid,solid&mark_type=none,none&mw=3,3&lw=2,2&ost=-99999,-99999&oet=99999,99999&mma=0,0&fml=a,a&fq=Monthly,Monthly&fam=avg,avg&fgst=lin,lin&fgsnd=2020-02-01,2020-02-01&line_index=1,2&transformation=lin,lin&vintage_date=2020-09-16,2020-10-16&nd=2001-01-01,2001-01-01", "MRTSSM44511USN_20201016")
# P.percentages(1, "MRTSSM44511USN_20201016")
# P.stacked(1, "MRTSSM44511USN_20201016")

# P.d_yfi(2, "^VIX")
# P.percentages(2, "close")
# P.inverse(2, "close")
# P.add(2, "close", 0.02)
# P.stacked(2, "close")

P.d_yfi(2, "wow.ax")
# P.percentages(2, "close")
# P.stacked(2, "close")

# P.d_yfi(3, "col.ax")
# P.percentages(3, "close")
# P.stacked(3, "close")

# P.dataset(2, {
#     "url":              "^VIX.yfi",
#     "range":            "daily",
#     "name":             "VIX",
#     "index":            "date",
#     "subsets":          ["close"],
#     "scrape_every":     "1 day"
# })
# P.sma(2, "close", period=5)

P.minimize([1, 2], normalize=True)

# our "callables" for date parsing our datasets

def nyfed_dp(input):
    s = str(input).split(":")[0].split("T")[0]
    return parse("year-month-day", s, normalize=True)

def yahoofin_dp(input):
    return parse("year-month-day", str(input), normalize=True)

def fred(input):
    return parse("year-month-day", str(input.split(" ")[0]), normalize=True)

def ppi(input):
    return parse("year-month-day", str(input.split(" ")[0]), normalize=True)

P.parse_indexes_as_date([
    [1, fred],
    [2, yahoofin_dp],
    # [3, yahoofin_dp]
])

# Meta-creators
mid = P.index([2], by=1)
print(P.meta[mid]["container"][0:5])
mid = P.clean(mid)
mid = P.floats(mid)
mid = P.same_start(mid)

# print(P.meta[mid]["headers"])
# print(P.meta[mid]["container"][0])

P.meta_line_chart("./../bridges/supermarkets.bridge.json", {
    "use": mid,
    "bottom": 0,
    "left": [1],
    "right": [2],
    "names": ["string:Date", "number:Supermarket", "number:Woolworths"]
})
