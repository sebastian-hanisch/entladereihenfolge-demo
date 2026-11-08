"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds. Damit prüft der Test die Grenzen (kleiner als nach Rundung auf zwei Stellen, Gleichstand) und jede genannte Zahl direkt."""

import elr_constants as C
import elr_evaluation as ev
from elr_scenario import Instance

G, SA, SU, V = C.GRUNDFLAECHE, C.STOPP_AB, C.STOPP_AUF, C.VOLUMEN


def _tab(werte):
    """5 x 4 Tabelle (Schlüssel x Bedingung): werte = {(schluessel, spalte): Zahl}, sonst 5."""
    return tuple(tuple(werte.get((k, c), 5) for c in range(4)) for k in range(5))


def _a(schluessel=G, count=2, ohne=1, opt=1, tab=None, schranke=1, verletzung_ohne=(0, 0, 0), m_index=2, q_index=1, anwenden=1, entladen=0, entladen_zahl=0, entladen_blockiert=0, n=12):
    inst = Instance(((5, 5, 5),) * n, (), (), 100)
    s = ev.Settings(schluessel=schluessel, m_index=m_index, q_index=q_index, anwenden=anwenden, entladen=entladen)
    return ev.Analysis(inst, (1,) * n, (True,) * n, tuple(range(n)), n, (), (), (), 0, count, ohne, schranke, opt, tab or _tab({}), (0, 0, 0), verletzung_ohne, entladen_blockiert, entladen_zahl, 0.8, s)


def test_aktuell_kostet_ist_eine_warnung_und_nennt_den_besseren_schluessel():
    t = _tab({(V, 3): 2, (G, 3): 1, (SA, 3): 2})
    kind, text = ev.verdict_aktuell(_a(V, 2, 1, 1, t))
    assert kind == "warning"
    assert text == ("Nach dem Volumen sortiert und mit 3 Stopps und 20 % nicht stapelbar gesetzt brauchen die Quader **2** Behälter, ohne Bedingung 1. Die Bedingungen kosten hier 1. "
                    "Das Optimum ohne Stützbedingung ist **1** (die Schranke ist 1). Für beide Bedingungen ist in der Tabelle Grundfläche besser (1).")


def test_aktuell_kostet_nichts_und_spart_und_das_optimum_unbekannt():
    t = _tab({(G, 3): 1})
    kind, text = ev.verdict_aktuell(_a(G, 1, 1, 1, t))
    assert kind == "info" and "Die Bedingungen kosten hier nichts." in text and "Das ist das Optimum ohne Stützbedingung (die Schranke allein ergäbe 1)." in text
    assert "Für beide Bedingungen ist das einer der besten Schlüssel dieser Instanz." in text
    kind, text = ev.verdict_aktuell(_a(G, 1, 2, None, t, 2))
    assert kind == "success" and "Die Bedingungen sparen hier 1 (die Platzierung der Quader ändert sich)." in text and "Ein Optimum ist für diese Instanz nicht berechnet; die Schranke ist 2." in text


def test_aktuell_ohne_beachtung_und_der_bedingungstext():
    kind, text = ev.verdict_aktuell(_a(G, 1, 1, 1, anwenden=0))
    assert kind == "info" and text.startswith("Nach der Grundfläche sortiert und ohne Beachtung der Bedingungen brauchen die Quader **1** Behälter.") and text.endswith("Die Verletzungen stehen im Abschnitt unten.")
    assert ev.bedingungstext(ev.Settings(m_index=0, q_index=0)) == "keine Entlade- und Stapelbedingung"
    assert ev.bedingungstext(ev.Settings(m_index=1, q_index=0)) == "2 Stopps" and ev.bedingungstext(ev.Settings(m_index=0, q_index=2)) == "40 % nicht stapelbar"
    assert ev.bedingungstext(ev.Settings(m_index=3, q_index=1)) == "5 Stopps und 20 % nicht stapelbar"


def test_tabellenverdikt_drei_faelle():
    kind, text = ev.verdict_tabelle(_a(tab=_tab({(SA, 3): 2, (SU, 3): 4, (G, 3): 3})))
    assert kind == "success" and text == ("Mit beiden Bedingungen braucht Stopp ab **2** Behälter, Stopp auf (Gegenprobe) 4, die Grundfläche ohne Rücksicht auf den Stopp 3. Hier hilft es, nach dem Stopp zu sortieren.")
    kind, text = ev.verdict_tabelle(_a(tab=_tab({(SA, 3): 3, (SU, 3): 3, (G, 3): 3})))
    assert kind == "info" and text.endswith("Hier bringt das Sortieren nach dem Stopp nichts.")
    kind, text = ev.verdict_tabelle(_a(tab=_tab({(SA, 3): 4, (SU, 3): 6, (G, 3): 3})))
    assert kind == "warning" and "Mit beiden Bedingungen braucht Stopp ab **4** Behälter, Stopp auf (Gegenprobe) 6, die Grundfläche ohne Rücksicht auf den Stopp 3." in text and text.endswith("Hier **schadet** das Sortieren nach dem Stopp.")


def test_verletzungsverdikt_mit_und_ohne_verletzung():
    kind, text = ev.verdict_verletzung(_a(verletzung_ohne=(3, 1, 6)))
    assert kind == "warning"
    assert text == ("In der Packung ohne Bedingung blockieren **3** Paare (ein später zu entladender Quader liegt über einem früheren), und 1 Paare liegen über nicht stapelbaren Quadern; **6** von 12 Quadern sind betroffen. "
                    "Solche Packungen müssten beim Entladen umgestaut werden.")
    kind, text = ev.verdict_verletzung(_a(verletzung_ohne=(0, 1, 2)))
    assert kind == "warning" and "blockieren **0** Paare" in text and "1 Paare liegen über nicht stapelbaren" in text and "**2** von 12" in text
    kind, text = ev.verdict_verletzung(_a(verletzung_ohne=(0, 0, 0)))
    assert kind == "success" and "weder blockierte Paare noch Quader über nicht stapelbaren" in text


def test_entladenverdikt_drei_zweige_und_die_zahlen():
    kind, text = ev.verdict_entladen(_a(entladen=0))
    assert kind == "info" and text.startswith("Wählen Sie „Entladen bis Stopp“")
    kind, text = ev.verdict_entladen(_a(entladen=2, entladen_zahl=7, entladen_blockiert=0))
    assert kind == "success" and text == ("Nach dem Entladen der Stopps 1 bis 2 sind **7** von 12 Quadern entladen. Keiner davon lag unter einem Quader, der später entladen wird: Alle waren von oben frei.")
    kind, text = ev.verdict_entladen(_a(entladen=1, entladen_zahl=4, entladen_blockiert=2))
    assert kind == "warning" and text == ("Nach dem Entladen der Stopps 1 bis 1 sind **4** von 12 Quadern entladen. **2** davon lagen unter einem später zu entladenden Quader und müssten umgestaut werden.")


# --- Messraster ----------------------------------------------------------------------------------------------------------------------------


def _mittel(werte):
    return {k: {c: werte.get((k, c), 1.0) for c in range(6)} for k in range(5)}


def _z(werte=None, verteilung=0, n=40, verletzung=None, mehr=None):
    return {"verteilung": verteilung, "name": C.VERTEILUNG_LANG[verteilung], "n": n, "instanzen": 100, "mittel": _mittel(werte or {}),
            "mehr": mehr or {k: {c: 0 for c in range(1, 6)} for k in range(5)},
            "verletzung": verletzung or {c: {"paare": float(c), "nicht": 0.0, "quader": 10.0 * c} for c in range(1, 6)}}


def test_kosten_verdikt_nennt_alle_zahlen():
    kind, text = ev.verdict_kosten(_z({(G, 0): 1.58, (G, 2): 2.17, (G, 5): 3.03}))
    assert kind == "warning"
    assert text == ("Für mittlere Quader mit n = 40 braucht die Grundfläche über der Schranke ohne Bedingung 1.58 Behälter, mit 3 Stopps 2.17 und mit 3 Stopps und 40 % nicht stapelbar 3.03 (100 Instanzen). "
                    "Die Bedingungen kosten bis zu 1.45 Behälter im Mittel.")
    kind, text = ev.verdict_kosten(_z({}))
    assert kind == "info" and "kosten in dieser Zelle nichts" in text


def test_messung_verdikt_schlaegt_stopp_ab_die_grundflaeche():
    z = _z({(G, 0): 1.0, (SA, 0): 1.0, (SU, 0): 1.0, (V, 0): 1.2, (C.LIEFERUNG, 0): 2.0, (G, 1): 1.5, (SA, 1): 1.6, (SU, 1): 1.8, (V, 1): 1.9, (C.LIEFERUNG, 1): 2.1,
            (G, 2): 1.7, (SA, 2): 1.6, (SU, 2): 2.0, (V, 2): 2.0, (C.LIEFERUNG, 2): 2.4, (G, 3): 1.9, (SA, 3): 2.0, (SU, 3): 2.2, (V, 3): 2.3, (C.LIEFERUNG, 3): 2.6,
            (G, 4): 2.0, (SA, 4): 2.1, (SU, 4): 2.4, (V, 4): 2.5, (C.LIEFERUNG, 4): 2.7, (G, 5): 2.5, (SA, 5): 2.6, (SU, 5): 2.9, (V, 5): 3.0, (C.LIEFERUNG, 5): 3.2})
    kind, text = ev.verdict_messung(z)
    assert kind == "success"
    assert text == ("Für mittlere Quader mit n = 40 ist der beste Schlüssel je Bedingung (Mittel über 100 Instanzen): ohne Bedingung Grundfläche und Stopp ab und Stopp auf; m = 2 Grundfläche; m = 3 Stopp ab; "
                    "m = 5 Grundfläche; m = 3, q = 0,2 Grundfläche; m = 3, q = 0,4 Grundfläche. Der Schlüssel Stopp ab schlägt die Grundfläche bei m = 3.")
    kind, text = ev.verdict_messung(_z({(G, c): 1.0 for c in range(6)}))
    assert kind == "info" and "alle gleich" in text and "schlägt die Grundfläche in keiner Kombination" in text


def test_messung_gleich_nach_rundung_ist_kein_schlagen():
    z = _z({(G, 2): 1.504, (SA, 2): 1.496})                                       # beide 1,50 nach Rundung
    kind, text = ev.verdict_messung(z)
    assert kind == "info"
    kind, text = ev.verdict_messung(_z({(G, 2): 1.506, (SA, 2): 1.494}))        # 1,51 gegen 1,49
    assert kind == "success" and "bei m = 3" in text


def test_verletzungsraster_verdikt_prozente():
    v = {1: {"paare": 3.2, "nicht": 0.0, "quader": 26.0}, 2: {"paare": 4.24, "nicht": 0.0, "quader": 33.4}, 3: {"paare": 5.0, "nicht": 0.0, "quader": 38.6}, 4: {"paare": 4.2, "nicht": 2.3, "quader": 43.0},
         5: {"paare": 4.2, "nicht": 4.7, "quader": 52.0}}
    kind, text = ev.verdict_verletzung_raster(_z(verletzung=v))
    assert kind == "warning"
    assert text == ("Für mittlere Quader mit n = 40 sind in der Packung ohne Bedingung bei 2 Stopps 26 %, bei 3 Stopps 33 % und bei 5 Stopps 39 % der Quader von einer Blockierung betroffen "
                    "(im Mittel 4.2 blockierte Paare bei 3 Stopps). Je mehr Stopps, desto mehr Quader müssten beim Entladen umgestaut werden.")


def _oz(v, q, ohne, mit, heur_ohne, heur_mit, entschieden=40, offen=0):
    return {"verteilung": v, "q": q, "instanzen": 40, "entschieden": entschieden, "offen": offen, "ohne": ohne, "mit": mit, "gleich": 30, "mehr": 10, "heur_ohne": heur_ohne, "heur_mit": heur_mit, "trifft": 20}


def test_orakel_verdikt_vergleicht_den_mehrbedarf_von_optimum_und_heuristik():
    zeilen = [_oz(0, 0.0, 1.5, 1.5, 2.0, 2.2), _oz(1, 0.0, 1.5, 1.6, 2.0, 2.4), _oz(0, 0.4, 1.5, 1.8, 2.0, 2.3), _oz(1, 0.4, 1.5, 1.9, 2.0, 2.6)]
    kind, text = ev.verdict_orakel(zeilen)
    assert kind == "info"
    assert text == ("Im Optimum kostet die Entladereihenfolge allein bei 3 Stopps im Mittel +0.05 Behälter, mit 40 % nicht stapelbar +0.35; in der Heuristik sind es +0.30 beziehungsweise +0.45 "
                    "(Mittel über die vier Verteilungen, n = 12, ohne Stützbedingung). Die Heuristik zahlt mehr für die Bedingungen, als die Aufgabe verlangt.")
    zeilen2 = [_oz(0, 0.0, 1.5, 1.7, 2.0, 2.1), _oz(0, 0.4, 1.5, 2.0, 2.0, 2.2)]
    assert ev.verdict_orakel(zeilen2)[1].endswith("Die Heuristik zahlt nicht mehr als das Optimum.")


def test_zeile_rechnet_mittel_und_prozente_aus_den_summen():
    uebers = {str(k): {str(c): 4 * (k + c + 1) for c in range(6)} for k in range(5)}
    mehr = {str(k): {str(c): k + c for c in range(1, 6)} for k in range(5)}
    verl = {str(c): {"paare": 8 * c, "nicht": 4 * c, "quader": 2 * c} for c in range(1, 6)}
    daten = {"instanzen": 4, "cap": 100, "zellen": {"mittel|20": {"ueber_schranke": uebers, "mehr_als_ohne": mehr, "verletzung": verl}}}
    z = ev.zeile(0, 0, daten)
    assert z["n"] == 20 and z["instanzen"] == 4 and z["mittel"][2][3] == 4 * 6 / 4 and z["mehr"][4][5] == 9
    assert z["verletzung"][2] == {"paare": 4.0, "nicht": 2.0, "quader": 100.0 * 4 / (20 * 4)}
    assert ev.gerundet({k: {0: 1.005, 1: 2.0} for k in range(5)})[0][1] == 2.0


def test_orakelzeilen_aus_den_gespeicherten_summen():
    daten = {"instanzen": 100, "orakel": {f"{name}|{qi}": {"instanzen": 40, "entschieden": 4, "offen": 1, "ohne": 6, "mit": 8, "gleich": 3, "mehr": 1, "heur_ohne": 10, "heur_mit": 12, "trifft": 2}
                                           for qi in range(len(C.ORAKEL_Q)) for name, *_x in C.VERTEILUNGEN}}
    zeilen = ev.orakel_zeilen(daten)
    assert len(zeilen) == 12 and [(z["q"], z["verteilung"]) for z in zeilen][:5] == [(0.0, 0), (0.0, 1), (0.0, 2), (0.0, 3), (0.2, 0)]
    assert zeilen[0]["ohne"] == 1.5 and zeilen[0]["mit"] == 2.0 and zeilen[0]["heur_ohne"] == 2.5 and zeilen[0]["heur_mit"] == 3.0 and zeilen[0]["offen"] == 1 and zeilen[0]["trifft"] == 2
