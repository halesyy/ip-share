from packer import Packer
from fdates import parse

P = Packer()

P.d_csv(
    1,
    url="https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=UNRATE&scale=left&cosd=1948-01-01&coed=2020-09-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2020-10-29&revision_date=2020-10-29&nd=1948-01-01",
    index="DATE",
    subset="UNRATE",
    name="number:Unemployment"
)
P.percentages(1, "UNRATE")
P.stacked(1, "UNRATE", inverse=True)

P.d_csv(
    2,
    url="https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=INDPRO&scale=left&cosd=1919-01-01&coed=2020-09-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2020-10-29&revision_date=2020-10-29&nd=1919-01-01",
    index="DATE",
    subset="INDPRO",
    name="number:Industrial Production"
)
P.percentages(2, "INDPRO")
P.stacked(2, "INDPRO", inverse=True)

# P.d_csv(
#     3,
#     url="https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=BAMLH0A0HYM2&scale=left&cosd=2015-10-28&coed=2020-10-28&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily%2C%20Close&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2020-10-29&revision_date=2020-10-29&nd=1996-12-31",
#     index="DATE",
#     subset="BAMLH0A0HYM2",
#     name="number:Option Spreads"
# )
# P.remove_dots(3, "BAMLH0A0HYM2")
# P.percentages(3, "BAMLH0A0HYM2")
# P.stacked(3, "BAMLH0A0HYM2", inverse=True)


# P.d_yfi(2, "^VIX", name="number:VIX")

# P.d_yfi(2, "^GSPC", name="number:S&P")

P.minimize(P.ids, normalize=True)

def fred(input):
    return parse("year-month-day", str(input.split(" ")[0]), normalize=True)

def yfi(input):
    return parse("year-month-day", str(input), normalize=True)

P.parse_indexes_as_date([
    [1, yfi],
    [2, yfi],
    # [3, yfi],
    # [3, yfi]
])

# Meta-creators
mid = P.index([2], by=1)
mid = P.clean(mid)

P.meta_line_chart("./../bridges/unemployment.bridge.json", {
    "use": mid,
    "bottom": 0,
    "random": P.ids,
    "names": P.names
})
