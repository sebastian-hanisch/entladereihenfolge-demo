"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (elr_precomputed.json): jede Zelle bei n = 20 frisch gerechnet, bei allen Zellen die ersten drei Instanzen einzeln (Stichprobe in der Datei); alle Zellen vollständig prüft
  `python generate_precomputed.py --check` (parallel). Das Orakel wird an einer Stichprobe der Instanzen und an einer ganzen Zelle mit CP-SAT noch einmal gerechnet.
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt."""

import itertools
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest

import elr_algorithm as A
import elr_constants as C
import elr_evaluation as ev
from elr_scenario import beispiel, mess_seed, zufallsinstanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(range(len(C.VERTEILUNGEN)), range(len(C.MESS_N))))
L, V, G, SA, SF = C.LIEFERUNG, C.VOLUMEN, C.GRUNDFLAECHE, C.STOPP_AB, C.STOPP_AUF


def alle():
    return {(v, ni): ev.zeile(v, ni) for v, ni in ZELLEN}


def gerundete():
    return {k: ev.gerundet(z["mittel"]) for k, z in alle().items()}


def test_raster_hat_alle_zellen_und_die_parameter():
    daten = ev.vorberechnet()
    assert daten["instanzen"] == 100 and daten["cap"] == C.CAP == 100 and len(ZELLEN) == 12
    assert set(daten["zellen"]) == {ev.zelle_schluessel(v, ni) for v, ni in ZELLEN}
    assert set(daten["stichprobe"]) == set(daten["zellen"])
    assert set(daten["orakel"]) == {f"{name}|{qi}" for qi in range(len(C.ORAKEL_Q)) for name, *_x in C.VERTEILUNGEN}
    assert C.MESS_N == (20, 40, 80) and C.KOMBIS == ((2, 0), (3, 0), (5, 0), (3, 0.2), (3, 0.4)) and C.MESS_SMIN == 0.8


def _addiere(a, b):
    if isinstance(a, dict):
        return {k: _addiere(a[k], b[k]) for k in a}
    return a + b


def _nicht_kleiner(a, b):
    if isinstance(a, dict):
        return all(_nicht_kleiner(a[k], b[k]) for k in a)
    return a >= b


@pytest.mark.parametrize("v", range(len(C.VERTEILUNGEN)))
def test_jede_zelle_bei_n_20_stimmt_mit_frischer_rechnung(v):
    ni = C.MESS_N.index(20)
    assert ev.messzelle(v, ni) == ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_stichprobe_jeder_zelle_stimmt_mit_frischer_rechnung(v, ni):
    schl = ev.zelle_schluessel(v, ni)
    daten = ev.vorberechnet()
    summe = None
    for j in C.STICHPROBE_J:
        gespeichert = daten["stichprobe"][schl][str(j)]
        assert ev.messzelle(v, ni, [j]) == gespeichert, (schl, j)
        summe = gespeichert if summe is None else {k: _addiere(summe[k], gespeichert[k]) for k in gespeichert}
    zelle = daten["zellen"][schl]
    for k in summe:                          # die Stichprobe ist Teil der Zelle: jede Summe der Zelle ist mindestens so groß (alle Beiträge sind nicht negativ)
        assert _nicht_kleiner(zelle[k], summe[k]), (schl, k)


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_summen_sind_in_sich_stimmig(v, ni):
    z = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]
    n, k = C.MESS_N[ni], C.INSTANZEN
    for kk in "01234":
        assert all(z["mehr_als_ohne"][kk][c] <= k for c in "12345")
    # Ohne Bedingung haben alle Stopps den Wert 1: Grundfläche, Stopp ab und Stopp auf sortieren gleich und packen dieselbe Menge.
    assert z["ueber_schranke"]["2"]["0"] == z["ueber_schranke"]["3"]["0"] == z["ueber_schranke"]["4"]["0"]
    for c in "12345":
        r = z["verletzung"][c]
        assert 0 <= r["quader"] <= n * k and r["paare"] >= 0 and r["nicht"] >= 0
    assert z["verletzung"]["1"]["nicht"] == z["verletzung"]["2"]["nicht"] == z["verletzung"]["3"]["nicht"] == 0           # ohne nicht stapelbare Quader gibt es keine Paare darüber
    assert z["verletzung"]["2"]["paare"] == z["verletzung"]["4"]["paare"] == z["verletzung"]["5"]["paare"]                   # dieselben 3 Stopps
    assert z["verletzung"]["5"]["nicht"] >= z["verletzung"]["4"]["nicht"] >= 0
    assert z["verletzung"]["1"]["paare"] <= z["verletzung"]["2"]["paare"] <= z["verletzung"]["3"]["paare"]                   # mehr Stopps, mehr blockierte Paare


def test_ohne_bedingung_sind_grundflaeche_stopp_ab_und_stopp_auf_gleich():
    g = gerundete()
    assert all(x[G][0] == x[SA][0] == x[SF][0] for x in g.values())
    assert all(x[L][0] > x[G][0] and x[V][0] > x[G][0] for x in g.values())
    assert "Ohne Bedingung sind Grundfläche, Stopp ab und Stopp auf gleich (alle Stopps sind 1, die Packung ist dieselbe)" in README


# --- Orakel ---------------------------------------------------------------------------------------------------------------------------------------


def test_orakel_in_sich_stimmig():
    daten = ev.vorberechnet()["orakel"]
    assert len(daten) == 12
    for name, z in daten.items():
        assert z["instanzen"] == C.ORAKEL_INSTANZEN == 40 and z["entschieden"] + z["offen"] == 40 and z["gleich"] + z["mehr"] == z["entschieden"]
        assert z["mit"] >= z["ohne"] >= z["entschieden"] and z["heur_ohne"] >= z["ohne"] and z["heur_mit"] >= z["mit"] and 0 <= z["trifft"] <= z["entschieden"], name
        assert z["mit"] - z["ohne"] >= z["mehr"]                              # jede Instanz mit „mehr“ kostet mindestens einen Behälter


def test_orakel_stichprobe_und_eine_ganze_zelle_mit_cpsat():
    pytest.importorskip("ortools")
    from generate_precomputed import _orakel_zelle, orakel_instanz

    for v in range(len(C.VERTEILUNGEN)):
        for j in range(3):
            ohne, mit, h_ohne, h_mit = orakel_instanz(v, 2, j)
            assert 1 <= ohne <= mit <= h_mit and ohne <= h_ohne <= h_mit, (v, j)
    name, z = _orakel_zelle((2, 2))                                         # kleine Quader, 40 % nicht stapelbar: schnell zu rechnen
    assert name == "klein|2" and z == ev.vorberechnet()["orakel"]["klein|2"]


def test_orakel_zahlen_der_readme():
    zeilen = ev.orakel_zeilen()
    assert len(zeilen) == 12 and sum(r["instanzen"] for r in zeilen) == 480 and sum(r["entschieden"] for r in zeilen) == 480 and sum(r["offen"] for r in zeilen) == 0
    mehr = {q: sum(r["mehr"] for r in zeilen if r["q"] == q) for q in C.ORAKEL_Q}
    assert mehr == {0.0: 5, 0.2: 38, 0.4: 63} and all(sum(r["entschieden"] for r in zeilen if r["q"] == q) == 160 for q in C.ORAKEL_Q)
    assert sum(r["trifft"] for r in zeilen) == 286
    klein = [r for r in zeilen if r["verteilung"] == 2]
    assert sum(r["mehr"] for r in klein) == 0 and sum(r["entschieden"] for r in klein) == 120
    flach = [r for r in zeilen if r["verteilung"] == 3 and r["q"] == 0.4][0]
    assert (flach["mehr"], flach["entschieden"], round(flach["ohne"], 2), round(flach["mit"], 2)) == (36, 40, 1.62, 3.33)
    assert ev.verdict_orakel(zeilen)[0] == "info" and "+0.04 Behälter, mit 40 % nicht stapelbar +0.60; in der Heuristik sind es +0.23 beziehungsweise +0.75" in ev.verdict_orakel(zeilen)[1]
    for text in ("alle 480 Instanzen entschieden): Im Optimum brauchen die Bedingungen in **5** von 160 Instanzen mehr Behälter, wenn alle stapelbar sind, in **38** von 160 bei 20 % und in **63** von 160 bei 40 % nicht stapelbar",
                 "Kleine Quader kosten nie etwas (0 von 120), flache am meisten (bei 40 %: 36 von 40, im Mittel 1,62 → 3,33 Behälter)",
                 "trifft das Optimum mit Bedingungen in **286** von 480 Instanzen. Im Mittel kosten die Bedingungen im Optimum +0,04 (3 Stopps) beziehungsweise +0,60 (mit 40 % nicht stapelbar) Behälter, in der Heuristik +0,23 beziehungsweise +0,75"):
        assert text in README, text


# --- Beispiele ------------------------------------------------------------------------------------------------------------------------------------


def test_beispiele_sind_zufallsinstanzen_mit_dem_optimum_von_cpsat():
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    for b, (v, seed) in enumerate(((1, 7_001_114), (0, 7_000_004))):
        inst = zufallsinstanz(v, 12, seed)
        ref = beispiel(b)
        assert inst.kisten == ref.kisten and inst.u == ref.u and inst.w == ref.w
        for m, q in itertools.product(C.M_WERTE, C.Q_WERTE):
            stopp, stap = ref.stopps(m), ref.stapelbar(q)
            ober = len(A.pack(ref.kisten, stopp, stap, A.reihenfolge(ref.kisten, stopp, G), ref.cap, 0.0)[0])
            assert optimum_cpsat(ref.kisten, stopp, stap, ref.cap, ober, True, 60.0, 2) == C.BEISPIEL_OPTIMUM[b] == 1, (b, m, q)


def test_beispiel_tabellen_in_der_readme():
    t1, t2 = ev.tabelle(beispiel(0), 3, 0.2, C.MESS_SMIN), ev.tabelle(beispiel(1), 3, 0.2, C.MESS_SMIN)
    assert [list(r) for r in t1] == [[1, 1, 2, 2], [1, 1, 1, 2], [1, 1, 1, 1], [1, 1, 1, 2], [1, 2, 1, 2]]
    assert [list(r) for r in t2] == [[2, 2, 2, 2], [1, 2, 1, 2], [1, 1, 1, 2], [1, 2, 1, 2], [1, 2, 1, 2]]
    assert "Ohne Bedingung brauchen alle fünf Schlüssel **1** Behälter. Mit 3 Stopps und 20 % nicht stapelbar bleibt **nur die Grundfläche bei 1**, die anderen vier brauchen 2" in README
    assert "Lieferung kostet schon die Stapelbarkeit allein einen Behälter, Stopp auf schon die Entladereihenfolge allein" in README
    assert "Die Grundfläche braucht ohne Bedingung 1, mit der Entladereihenfolge allein 1, mit der Stapelbarkeit allein 1, mit **beiden 2**" in README
    assert "Beispiel 1 (zwölf breit gestreute Quader, Optimum 1)" in README and "Beispiel 2 (zwölf mittlere Quader, Optimum 1)" in README


# --- Befunde der README --------------------------------------------------------------------------------------------------------------------


def _mittel_der_zellen():
    g = gerundete()
    return {k: {c: sum(x[k][c] for x in g.values()) / len(g) for c in range(6)} for k in range(5)}


def test_kosten_der_bedingungen():
    m = {k: {c: round(v, 2) for c, v in d.items()} for k, d in _mittel_der_zellen().items()}
    assert [round(m[G][c] - m[G][0], 2) for c in range(1, 6)] == [0.30, 0.48, 0.66, 1.27, 2.27]
    assert [round(m[SA][c] - m[SA][0], 2) for c in range(1, 6)] == [0.44, 0.64, 0.84, 1.55, 2.62]
    assert "mit der Grundfläche **+0,30 / +0,48 / +0,66 / +1,27 / +2,27** Behälter bei 2 Stopps, 3 Stopps, 5 Stopps, 3 Stopps mit 20 % und 3 Stopps mit 40 % nicht stapelbar (Tabelle B)" in README
    assert "Stopp ab kostet im Mittel +0,44 / +0,64 / +0,84 / +1,55 / +2,62 Behälter" in README
    g = gerundete()
    assert max(g, key=lambda k: g[k][G][5] - g[k][G][0]) == (3, 2) and (g[(3, 2)][G][0], g[(3, 2)][G][5]) == (4.01, 13.48)
    assert "n = 80, 3 Stopps und 40 %: 4,01 → 13,48" in README


def test_instanz_fuer_instanz_zaehlungen():
    z = alle()
    assert sum(C.INSTANZEN for _ in z) == 1200
    assert [sum(x["mehr"][G][c] for x in z.values()) for c in range(1, 6)] == [373, 512, 620, 798, 990]
    assert [sum(x["mehr"][SA][c] for x in z.values()) for c in range(1, 6)] == [500, 647, 760, 908, 1051]
    assert "in **373 / 512 / 620 / 798 / 990** mehr Behälter als ohne Bedingung, Stopp ab in **500 / 647 / 760 / 908 / 1051**" in README and "Von 1200 Instanzen" in README


def test_bester_schluessel_mit_bedingung():
    g = gerundete()
    allein = {c: sum(1 for x in g.values() if ev.beste_schluessel_zelle(x, c) == [G]) for c in range(1, 6)}
    assert allein == {1: 11, 2: 8, 3: 9, 4: 11, 5: 12}
    assert "Grundfläche allein der beste Schlüssel in **11 / 8 / 9 / 11 / 12** von 12 Zellen" in README
    besser = {c: sum(1 for x in g.values() if x[SA][c] < x[G][c]) for c in range(1, 6)}
    assert besser == {1: 0, 2: 2, 3: 3, 4: 0, 5: 0} and "Stopp ab schlägt sie nur bei 3 Stopps (in 2 Zellen) und bei 5 Stopps (in 3 Zellen), bei den anderen drei Bedingungen nie" in README
    for c in range(1, 6):
        assert all(x[V][c] > min(x[k][c] for k in range(5)) and x[L][c] > min(x[k][c] for k in range(5)) and x[SF][c] > min(x[k][c] for k in range(5)) for x in g.values()), c
    assert "Volumen und Lieferung sind in jeder Zelle schlechter, Stopp auf (Gegenprobe) ebenso" in README


def r1(x: float) -> float:
    """Auf eine Stelle gerundet, .x5 nach oben (so schreibt die README: 28,15 -> 28,2)."""
    return float(Decimal(str(round(x, 6))).quantize(Decimal("0.1"), ROUND_HALF_UP))


def test_verletzungen_beim_ignorieren():
    z = alle()
    for c, (q_lo, q_hi, p_lo, p_hi) in {1: (19.5, 63.0, 2.3, 50.6), 2: (28.2, 74.1, 3.4, 66.3), 3: (33.5, 80.9, 4.1, 79.4)}.items():
        q = [x["verletzung"][c]["quader"] for x in z.values()]
        p = [x["verletzung"][c]["paare"] for x in z.values()]
        assert (r1(min(q)), r1(max(q)), r1(min(p)), r1(max(p))) == (q_lo, q_hi, p_lo, p_hi), c
    assert "**28,2 bis 74,1 %** der Quader von einer Blockierung betroffen, im Mittel **3,4 bis 66,3** blockierte Paare je Instanz (2 Stopps: 19,5 bis 63,0 % und 2,3 bis 50,6 Paare; 5 Stopps: 33,5 bis 80,9 % und 4,1 bis 79,4 Paare)" in README
    flach = z[(3, 2)]["verletzung"][2]
    assert (round(flach["paare"], 1), round(flach["quader"])) == (66.3, 74) and "(n = 80, 3 Stopps: 66,3 Paare, 74 %)" in README
    assert max(z, key=lambda k: z[k]["verletzung"][2]["quader"]) == (3, 2)


# --- Tabellen der README -------------------------------------------------------------------------------------------------------------------


def test_readme_tabellen_geben_jede_zeile_wieder():
    from dev.readme_bauen import tabellen

    for tabelle in tabellen():
        for zeile in tabelle.split("\n"):
            assert zeile in README, zeile


def test_readme_kennzahlen_stehen_in_der_readme():
    from dev.readme_bauen import kennzahlen

    k = kennzahlen()
    assert k["K_G1"] == "0,30" and k["S_5"] == "2,62" and k["M_G"] == "373 / 512 / 620 / 798 / 990" and k["B_G"] == "11 / 8 / 9 / 11 / 12"


# --- Texte ---------------------------------------------------------------------------------------------------------------------------------------


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    t = C.ASSUMPTIONS_MARKDOWN
    assert f"Behälter {C.CAP} mal {C.CAP} mal {C.CAP}" in t and f"{C.INSTANZEN} Instanzen" in t and "(20, 40, 80)" in t and f"{int(C.ORAKEL_ZEIT)} Sekunden Zeitlimit" in t and "nur bei 12 Quadern und 3 Stopps" in t
    assert C.MESS_N == (20, 40, 80) and C.ORAKEL_ZEIT == 20.0 and C.ORAKEL_N == 12 and C.ORAKEL_M == 3 and C.ORAKEL_Q == (0.0, 0.2, 0.4)


def test_readme_nennt_die_verteilungen_und_das_raster_wie_der_code():
    assert "*mittel* (alle Kanten 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *flach* (Breite und Tiefe 30 bis 80, Höhe 5 bis 30)" in README
    assert [vt[2] for vt in C.VERTEILUNGEN] == [((20, 60),) * 3, ((5, 70),) * 3, ((10, 40),) * 3, ((30, 80), (30, 80), (5, 30))]
    assert "vier Verteilungen × drei Quaderzahlen (20, 40, 80) × **100 feste Instanzen** je Zelle × fünf Schlüssel × sechs Bedingungen" in README
    assert "bei 12 Quadern 40 Instanzen je Verteilung und Anteil nicht stapelbar (0, 20, 40 %), 3 Stopps, CP-SAT mit 20 Sekunden Zeitlimit je Lauf" in README
    assert len(C.SCHLUESSEL) * len(C.BEDINGUNGEN) == 20 and "alle 20 Kombinationen aus Schlüssel und Bedingung" in README


def test_readme_hat_keine_offenen_platzhalter_ausser_dem_live_link():
    assert "{{" not in README and "TESTZAHL" not in README and README.count("TODO") == 1
    assert "<!-- TODO nach dem Deploy" in README and "https://sebastianhanisch-entladereihenfolge-demo.streamlit.app/" in README
