from packer import Packer
from fdates import parse

P = Packer()

# P.d_fred(1, "https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=NPPTTL&scale=left&cosd=2002-04-01&coed=2020-09-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2020-10-31&revision_date=2020-10-31&nd=2002-04-01", "NPPTTL")
# P.percentages(1, "NPPTTL")
# P.multiply(1, "NPPTTL")

# gold
P.d_fred(1, "https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=GVZCLS&scale=left&cosd=2008-06-03&coed=2020-10-29&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily%2C%20Close&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2020-10-31&revision_date=2020-10-31&nd=2008-06-03", "GVZCLS")
P.remove_dots(1, "GVZCLS")

# oil
P.d_fred(2, "https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=OVXCLS&scale=left&cosd=2007-05-10&coed=2020-10-29&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily%2C%20Close&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2020-10-31&revision_date=2020-10-31&nd=2007-05-10", "OVXCLS")
P.remove_dots(2, "OVXCLS")

# P.d_yfi(2, "^VIX")
# P.percentages(2, "close")
# P.inverse(2, "close")
# P.add(2, "close", 0.02)

P.minimize([1, 2], normalize=True)

# our "callables" for date parsing our datasets

def fred(input):
    return parse("year-month-day", str(input.split(" ")[0]), normalize=True)

P.parse_indexes_as_date([
    [1, fred],
    [2, fred],
    # [3, fred]
])

# Meta-creators
mid = P.index([2], by=1)
mid = P.clean(mid)
mid = P.floats(mid)
mid = P.same_start(mid)

print(P.meta[mid]["headers"])
print(P.meta[mid]["container"][0])

P.meta_line_chart("./../bridges/payroll.bridge.json", {
    "use": mid,
    "bottom": 0,
    "left": [1],
    "right": [2],
    "names": ["string:Date", "number:Gold", "number:Oil"]
})
