"""Plotly-Abbildungen: ein Behälter in 3D (Mesh3d) und das Messraster als Balken. Die Balkendiagramme haben gesperrte Achsen (fixedrange), damit Touch-Geräte beim Scrollen nicht hängen bleiben."""

import plotly.graph_objects as go

import elr_constants as C

# Ecken eines Quaders (x, y, z, w, d, h): 0 bis 3 unten ((x,y), (x+w,y), (x+w,y+d), (x,y+d)), 4 bis 7 darüber.
# Zwei Dreiecke je Seitenfläche: unten, oben, vorn (y), hinten (y + d), links (x), rechts (x + w).
DREIECKE = ((0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (3, 7, 6), (3, 6, 2), (0, 4, 7), (0, 7, 3), (1, 2, 6), (1, 6, 5))
KANTEN = ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7))


def ecken(x, y, z, w, d, h):
    return [(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z), (x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)]


def quader_mesh(x, y, z, w, d, h, farbe, name, text):
    e = ecken(x, y, z, w, d, h)
    return go.Mesh3d(x=[p[0] for p in e], y=[p[1] for p in e], z=[p[2] for p in e], i=[t[0] for t in DREIECKE], j=[t[1] for t in DREIECKE], k=[t[2] for t in DREIECKE],
                     color=farbe, opacity=0.85, flatshading=True, name=name, hovertext=text, hoverinfo="text", showlegend=False)


def kantenlinien(boxen, farbe, breite):
    """Alle Kanten der Quader (x, y, z, w, d, h) als eine Linie mit Lücken."""
    xs, ys, zs = [], [], []
    for b in boxen:
        e = ecken(*b)
        for a, c in KANTEN:
            xs += [e[a][0], e[c][0], None]
            ys += [e[a][1], e[c][1], None]
            zs += [e[a][2], e[c][2], None]
    return go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(color=farbe, width=breite), hoverinfo="skip", showlegend=False)


def quader_farbe(farbe: int, s: int, i: int, stopp, stapelbar) -> str:
    """Farbe von Quader i, der als s-ter gesetzt wurde: 0 nach der Reihenfolge des Setzens, 1 nach dem Stopp, 2 nach der Stapelbarkeit (grün stapelbar, rot nicht)."""
    if farbe == 1:
        return C.STOPP_FARBEN[(stopp[i] - 1) % len(C.STOPP_FARBEN)]
    if farbe == 2:
        return C.STAPEL_FARBEN[bool(stapelbar[i])]
    return C.KISTEN_FARBEN[s % len(C.KISTEN_FARBEN)]


def build_behaelter(kisten, platz, behaelter, cap, zustand, farbe, stopp, stapelbar, markiert=()):
    """Ein Behälter in 3D: der Rahmen rot, jeder Quader massiv, die Eckpunkte als grüne Rauten. `farbe` 0: Farbe nach der Reihenfolge des Setzens; 1: nach dem Stopp; 2: nach der Stapelbarkeit. Quader aus `markiert`
    (Nummern, die in einer Verletzung vorkommen) bekommen einen dicken roten Rand. Die Beschriftung beim Überfahren nennt die Nummer in der Lieferreihenfolge, die Maße, den Stopp und die Stapelbarkeit."""
    fig = go.Figure()
    fig.add_trace(kantenlinien([(0, 0, 0, cap, cap, cap)], C.COLOR_LINE, 4))
    gesetzt = [(s, p) for s, p in enumerate(platz) if p[1] == behaelter]
    for s, (i, _b, x, y, z) in gesetzt:
        w, d, h = kisten[i]
        fig.add_trace(quader_mesh(x, y, z, w, d, h, quader_farbe(farbe, s, i, stopp, stapelbar), f"Quader {i + 1}",
                                  f"Schritt {s + 1}: Quader {i + 1}, {w} × {d} × {h}, Ecke ({x}, {y}, {z}), Stopp {stopp[i]}, {'stapelbar' if stapelbar[i] else 'nicht stapelbar'}"))
    if gesetzt:
        fig.add_trace(kantenlinien([(x, y, z, *kisten[i]) for _s, (i, _b, x, y, z) in gesetzt], "white", 2))
    rot = [(x, y, z, *kisten[i]) for _s, (i, _b, x, y, z) in gesetzt if i in markiert]
    if rot:
        fig.add_trace(kantenlinien(rot, C.COLOR_LINE, 7))
    punkte = list(zustand)
    if punkte:
        fig.add_trace(go.Scatter3d(x=[p[0] for p in punkte], y=[p[1] for p in punkte], z=[p[2] for p in punkte], mode="markers", marker=dict(size=4, color=C.COLOR_PUNKT, symbol="diamond"),
                                   hovertext=[f"Eckpunkt ({p[0]}, {p[1]}, {p[2]})" for p in punkte], hoverinfo="text", showlegend=False))
    achse = dict(range=[0, cap], showbackground=False, showgrid=True, zeroline=False)
    fig.update_layout(height=460, margin=dict(l=0, r=0, t=0, b=0), scene=dict(xaxis=dict(title="x (Breite)", **achse), yaxis=dict(title="y (Tiefe)", **achse), zaxis=dict(title="z (Höhe)", **achse),
                                                                               aspectmode="cube", camera=dict(eye=dict(x=1.6, y=-1.6, z=1.0))))
    return fig


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def build_messung(mittel, titel):
    """Gruppierte Balken: je Bedingung (ohne, fünf Kombinationen) die mittleren Behälter über der Schranke für die fünf Schlüssel (mittel[schluessel][c])."""
    namen = ["ohne"] + [k.replace(" = ", "=") for k in C.KOMBI_KURZ]
    fig = go.Figure()
    for k in sorted(C.SCHLUESSEL):
        fig.add_trace(go.Bar(name=C.SCHLUESSEL_KURZ[k], x=namen, y=[mittel[k][c] for c in range(len(namen))], marker_color=C.VERFAHREN_FARBEN[k], hovertemplate="%{x}: %{y:.2f}<extra>" + C.SCHLUESSEL_KURZ[k] + "</extra>"))
    fig.update_layout(barmode="group", height=340, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.3), plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(title_text="Bedingung (m Stopps, q Anteil nicht stapelbar)")
    fig.update_yaxes(title_text=titel)
    return lock_axes(fig)
