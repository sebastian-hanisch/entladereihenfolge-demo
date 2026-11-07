"""3D-Darstellung: Die Dreiecke eines Quaders decken jede der sechs Seitenflächen lückenlos und ohne Überlappung ab; die Abbildung enthält genau die Quader, Eckpunkte und Markierungen, die sie zeigen soll;
die Farbe der Quader folgt dem Stopp, der Stapelbarkeit oder der Reihenfolge des Setzens."""

import elr_algorithm as A
import elr_constants as C
import elr_evaluation as ev
import elr_visualization as V

KISTEN = ((6, 4, 2), (4, 8, 3), (8, 4, 7), (3, 2, 5))
STOPP = (1, 2, 2, 2)
ALLE = (True, True, True, True)


def flaeche_dreieck(a, b, c):
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    kreuz = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    return (kreuz[0] ** 2 + kreuz[1] ** 2 + kreuz[2] ** 2) ** 0.5 / 2


def test_dreiecke_decken_jede_seitenflaeche_genau_zweimal_halb_ab():
    w, d, h = 3, 5, 7
    e = V.ecken(0, 0, 0, w, d, h)
    seiten = {"unten": w * d, "oben": w * d, "vorn": w * h, "hinten": w * h, "links": d * h, "rechts": d * h}
    ebenen = {"unten": lambda p: p[2] == 0, "oben": lambda p: p[2] == h, "vorn": lambda p: p[1] == 0, "hinten": lambda p: p[1] == d, "links": lambda p: p[0] == 0, "rechts": lambda p: p[0] == w}
    summe, anzahl = {n: 0.0 for n in seiten}, {n: 0 for n in seiten}
    for t in V.DREIECKE:
        pts = [e[i] for i in t]
        in_ebenen = [n for n in seiten if all(ebenen[n](p) for p in pts)]
        assert len(in_ebenen) == 1, t
        anzahl[in_ebenen[0]] += 1
        summe[in_ebenen[0]] += flaeche_dreieck(*pts)
    assert len(V.DREIECKE) == 12
    for n, flaeche in seiten.items():
        assert anzahl[n] == 2 and abs(summe[n] - flaeche) < 1e-9, n


def test_dreiecke_einer_seite_ueberlappen_nicht_und_die_kanten_verbinden_benachbarte_ecken():
    for a in range(0, 12, 2):
        s1, s2 = set(V.DREIECKE[a]), set(V.DREIECKE[a + 1])
        assert len(s1 & s2) == 2 and len(s1 | s2) == 4
    e = V.ecken(0, 0, 0, 2, 3, 4)
    assert all(sum(1 for i in range(3) if e[a][i] != e[b][i]) == 1 for a, b in V.KANTEN) and len({frozenset(k) for k in V.KANTEN}) == 12


def test_quaderfarbe_nach_stopp_stapelbarkeit_und_reihenfolge():
    stapel = (True, False, True, True)
    assert [V.quader_farbe(1, 0, i, STOPP, stapel) for i in range(4)] == [C.STOPP_FARBEN[0], C.STOPP_FARBEN[1], C.STOPP_FARBEN[1], C.STOPP_FARBEN[1]]
    assert [V.quader_farbe(2, 0, i, STOPP, stapel) for i in range(4)] == [C.STAPEL_FARBEN[True], C.STAPEL_FARBEN[False], C.STAPEL_FARBEN[True], C.STAPEL_FARBEN[True]]
    assert [V.quader_farbe(0, s, 0, STOPP, stapel) for s in (0, 1, 10)] == [C.KISTEN_FARBEN[0], C.KISTEN_FARBEN[1], C.KISTEN_FARBEN[0]]
    assert V.quader_farbe(1, 0, 0, (6,), (True,)) == C.STOPP_FARBEN[0]                                       # Stopp 6 läuft um die Farbliste herum
    assert len(set(C.STOPP_FARBEN)) == len(C.STOPP_FARBEN) == 5 and C.STAPEL_FARBEN[True] != C.STAPEL_FARBEN[False]


def test_abbildung_enthaelt_quader_rahmen_eckpunkte_und_markierung():
    bins, platz, zustand = A.pack(KISTEN, (1, 1, 1, 1), ALLE, [0, 1, 2, 3], 10)
    fig = V.build_behaelter(KISTEN, platz, 0, 10, zustand[0], 1, STOPP, ALLE, markiert={0, 2})
    meshes = [t for t in fig.data if t.type == "mesh3d"]
    assert len(meshes) == 4 and all(len(m.x) == 8 and len(m.i) == 12 for m in meshes)
    assert [m.color for m in meshes] == [C.STOPP_FARBEN[0], C.STOPP_FARBEN[1], C.STOPP_FARBEN[1], C.STOPP_FARBEN[1]]
    rauten = [t for t in fig.data if t.type == "scatter3d" and t.mode == "markers"]
    assert len(rauten) == 1 and len(rauten[0].x) == len(zustand[0])
    linien = [t for t in fig.data if t.type == "scatter3d" and t.mode == "lines"]
    assert len(linien) == 3                                                                                   # Rahmen, weiße Kanten, rote Markierung
    rot = [t for t in linien if t.line.color == C.COLOR_LINE and t.line.width == 7]
    assert len(rot) == 1 and sum(1 for x in rot[0].x if x is None) == 2 * 12                                  # zwei Quader mit je zwölf Kanten
    ohne = V.build_behaelter(KISTEN, platz, 0, 10, zustand[0], 1, STOPP, ALLE)
    assert len([t for t in ohne.data if t.type == "scatter3d" and t.mode == "lines"]) == 2
    hover = [t.hovertext for t in meshes][2]
    assert "Quader 3" in hover and "Stopp 2" in hover and "stapelbar" in hover and "nicht stapelbar" not in hover
    assert "nicht stapelbar" in V.build_behaelter(KISTEN, platz, 0, 10, zustand[0], 2, STOPP, (True, True, False, True)).data[3].hovertext


def test_abbildung_zeigt_nur_den_gewaehlten_behaelter():
    bins, platz, zustand = A.pack(KISTEN, STOPP, ALLE, [0, 1, 2, 3], 10)            # [[0, 1, 3], [2]]
    assert len([t for t in V.build_behaelter(KISTEN, platz, 0, 10, zustand[0], 1, STOPP, ALLE).data if t.type == "mesh3d"]) == 3
    assert len([t for t in V.build_behaelter(KISTEN, platz, 1, 10, zustand[1], 1, STOPP, ALLE).data if t.type == "mesh3d"]) == 1


def test_leerer_behaelter_und_leerer_zustand_werfen_nicht():
    fig = V.build_behaelter((), [], 0, 10, (), 1, (), ())
    assert len([t for t in fig.data if t.type == "mesh3d"]) == 0 and len(fig.data) == 1


def test_messdiagramm_hat_je_schluessel_einen_balken_je_bedingung():
    m = {k: {c: float(k + c) for c in range(6)} for k in range(5)}
    fig = V.build_messung(m, "Titel")
    assert len(fig.data) == 5 and all(len(t.x) == 6 for t in fig.data)
    assert [t.name for t in fig.data] == [C.SCHLUESSEL_KURZ[k] for k in range(5)] and list(fig.data[1].y) == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0] and fig.data[0].x[0] == "ohne" and fig.data[0].x[4] == "m=3, q=0,2"
    assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


def test_abbildung_zur_analyse_der_app():
    a = ev.analyse(ev.Settings())
    fig = V.build_behaelter(a.inst.kisten, a.platz, a.gezeigt, a.inst.cap, a.zustand[a.gezeigt], a.settings.farbe, a.stopp, a.stapelbar)
    assert len([t for t in fig.data if t.type == "mesh3d"]) == a.inst.n          # Beispiel 1, Grundfläche: alle zwölf Quader in einem Behälter
