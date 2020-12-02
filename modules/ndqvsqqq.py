from packer import Packer
from fdates import parse

P = Packer()

P.d_yfi(1, "NDQ.AX")
P.percentages(1, "close")

# P.percentages(1, "close")
# P.stacked(1, "close")

# P.d_fred(2, "https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=OVXCLS&scale=left&cosd=2007-05-10&coed=2020-10-29&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily%2C%20Close&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2020-10-31&revision_date=2020-10-31&nd=2007-05-10", "OVXCLS")
# P.remove_dots(2, "OVXCLS")

P.d_yfi(2, "QQQ")
P.percentages(2, "close")
# print(P.datasets[1]["subsets"])
# P.stacked(2, "close")
# P.inverse(2, "close")
# P.add(2, "close", 0.02)
P.d_yfi(3, "NDQ.AX")

P.minimize([1, 2, 3], normalize=True)

# our "callables" for date parsing our datasets

def fred(input):
    return parse("year-month-day", str(input.split(" ")[0]), normalize=True)
def yahoofin_dp(input):
    return parse("year-month-day", str(input), normalize=True)
pass

P.parse_indexes_as_date([
    [1, yahoofin_dp],
    [2, yahoofin_dp],
    [3, yahoofin_dp],
    # [3, fred]
])

# Meta-creators
mid = P.index([2, 3], by=1)
# print(P.meta[mid]["container"])

mid = P.clean(mid)
mid = P.floats(mid)

last = 0.01
def dp(data):
    global last
    r = data
    if r[1] == 0:
        return last
    calc = abs(((r[2]-r[1])/r[1])*100)
    if calc > 50000:
        return last
    else:
        last = calc
    return calc

mid = P.meta_derive(mid, "percentage", dp)
# mid = P.same_start(mid)

print(P.meta[mid]["headers"])
# for row in P.meta[mid]["container"]: print(row)
# print(P.meta[mid]["container"])

P.meta_line_chart("./../bridges/ndqvsqqq.bridge.json", {
    "use": mid,
    "bottom": 0,
    "left": [3],
    "right": [4],
    "names": ["string:Date", "ignore:Australian QQQ", "ignore:Fucked QQQ", "number:NDQ", "number:Dislocation"]
})
