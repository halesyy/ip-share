from packer import Packer
from fdates import parse

P = Packer()

P.d_fred(1, "https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=RRSFS&scale=left&cosd=1992-01-01&coed=2020-09-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2020-10-29&revision_date=2020-10-29&nd=1992-01-01", "RRSFS")
P.percentages(1, "RRSFS")
P.multiply(1, "RRSFS", 100)
P.stacked(1, "RRSFS")

# P.d_yfi(2, "^VIX")
# P.percentages(2, "close")
# P.inverse(2, "close")
# P.add(2, "close", 0.02)


P.minimize([1], normalize=True)

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
    # [2, yahoofin_dp]
])

# Meta-creators
mid = P.index([1], by=1)
mid = P.clean(mid)
mid = P.floats(mid)
# mid = P.same_start(mid)

print(P.meta[mid]["headers"])
print(P.meta[mid]["container"][0])

P.meta_line_chart("./../bridges/sforecast.bridge.json", {
    "use": mid,
    "bottom": 0,
    "left": [1],
    # "right": [2],
    "names": ["string:Date", "number:Change"]
})
