"""Setzt die README zusammen: Tabellen und Text der Annahmen kommen aus denselben Funktionen wie in der App (nur zum Schreiben der README, nicht Teil der Laufzeit).

    python dev/readme_bauen.py [ANZAHL_TESTS]
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import elr_constants as C  # noqa: E402
import elr_evaluation as ev  # noqa: E402
from elr_scenario import beispiel  # noqa: E402


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def zellen():
    return [(v, ni) for v in range(len(C.VERTEILUNGEN)) for ni in range(len(C.MESS_N))]


def mittel_ueber_zellen(daten=None) -> dict:
    """Mittel der gerundeten Zellenwerte über alle zwölf Zellen: {Schlüssel: {Bedingung: Wert}}."""
    g = [ev.gerundet(ev.zeile(v, ni, daten)["mittel"]) for v, ni in zellen()]
    return {k: {c: sum(x[k][c] for x in g) / len(g) for c in range(len(C.KOMBIS) + 1)} for k in ev.SCHLUESSEL_LISTE}


def kennzahlen() -> dict:
    """Die Zahlen im Fließtext der README (Platzhalter K_G1 bis K_G5, S_1 bis S_5, M_G, M_S, B_G): Mehrbedarf aus den auf zwei Stellen gerundeten Werten der Tabelle B (so rechnet die Leserin nach)."""
    m = {k: {c: round(v, 2) for c, v in d.items()} for k, d in mittel_ueber_zellen().items()}
    g = {f"K_G{c}": de(round(m[C.GRUNDFLAECHE][c] - m[C.GRUNDFLAECHE][0], 2)) for c in range(1, 6)}
    g.update({f"S_{c}": de(round(m[C.STOPP_AB][c] - m[C.STOPP_AB][0], 2)) for c in range(1, 6)})
    daten = ev.vorberechnet()
    zs = [daten["zellen"][ev.zelle_schluessel(v, ni)] for v, ni in zellen()]
    g["M_G"] = " / ".join(str(sum(z["mehr_als_ohne"][str(C.GRUNDFLAECHE)][str(c)] for z in zs)) for c in range(1, 6))
    g["M_S"] = " / ".join(str(sum(z["mehr_als_ohne"][str(C.STOPP_AB)][str(c)] for z in zs)) for c in range(1, 6))
    gr = {k: ev.gerundet(ev.zeile(*k)["mittel"]) for k in zellen()}
    g["B_G"] = " / ".join(str(sum(1 for k in gr if ev.beste_schluessel_zelle(gr[k], c) == [C.GRUNDFLAECHE])) for c in range(1, 6))
    return g


def tabellen():
    """(A, B, C, D, Beispiel 1, Beispiel 2): A = Behälter über der Schranke je Zelle für die Grundfläche (ohne Bedingung und die fünf Kombinationen), B = Mittel über alle Zellen je Schlüssel und Bedingung,
    C = Verletzungen in der Packung ohne Bedingung je Zelle (3 Stopps), D = Orakel, die Beispiele = Behälterzahlen je Schlüssel und Bedingung (3 Stopps, 20 % nicht stapelbar)."""
    ta = ["| Verteilung | n | ohne | " + " | ".join(C.KOMBI_KURZ) + " |", "|---|---|---|" + "---|" * len(C.KOMBIS)]
    tc = ["| Verteilung | n | blockierte Paare je Instanz | betroffene Quader |", "|---|---|---|---|"]
    for v, ni in zellen():
        z = ev.zeile(v, ni)
        ta.append(f"| {C.VERTEILUNG_KURZ[v]} | {C.MESS_N[ni]} | " + " | ".join(de(z["mittel"][C.GRUNDFLAECHE][c]) for c in range(len(C.KOMBIS) + 1)) + " |")
        vl = z["verletzung"][2]
        tc.append(f"| {C.VERTEILUNG_KURZ[v]} | {C.MESS_N[ni]} | {de(vl['paare'], 1)} | {vl['quader']:.0f} % |")
    m = mittel_ueber_zellen()
    tb = ["| Schlüssel | ohne | " + " | ".join(C.KOMBI_KURZ) + " |", "|---|---|" + "---|" * len(C.KOMBIS)]
    for k in ev.SCHLUESSEL_LISTE:
        tb.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(de(m[k][c]) for c in range(len(C.KOMBIS) + 1)) + " |")
    td = ["| Verteilung | nicht stapelbar | Optimum ohne Bedingung | Optimum mit Bedingungen | mehr Behälter im Optimum | Heuristik ohne | Heuristik mit | Heuristik trifft das Optimum |", "|---|---|---|---|---|---|---|---|"]
    for r in ev.orakel_zeilen():
        td.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} | {round(100 * r['q'])} % | {de(r['ohne'])} | {de(r['mit'])} | {r['mehr']} von {r['entschieden']} | {de(r['heur_ohne'])} | {de(r['heur_mit'])} | {r['trifft']} |")
    bsp = []
    for b in (0, 1):
        t = ev.tabelle(beispiel(b), 3, 0.2, C.MESS_SMIN)
        zeilen = ["| Schlüssel | " + " | ".join(C.BEDINGUNGEN[c] for c in ev.BEDINGUNG_LISTE) + " |", "|---|---|---|---|---|"]
        for k in ev.SCHLUESSEL_LISTE:
            zeilen.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(str(t[k][c]) for c in ev.BEDINGUNG_LISTE) + " |")
        bsp.append("\n".join(zeilen))
    return "\n".join(ta), "\n".join(tb), "\n".join(tc), "\n".join(td), bsp[0], bsp[1]


if __name__ == "__main__":
    vorlage = (ROOT / "dev" / "readme_vorlage.md").read_text(encoding="utf-8")
    ta, tb, tc, td, b1, b2 = tabellen()
    anzahl = sys.argv[1] if len(sys.argv) > 1 else "TESTZAHL"
    text = (vorlage.replace("{{TABELLE_A}}", ta).replace("{{TABELLE_B}}", tb).replace("{{TABELLE_C}}", tc).replace("{{TABELLE_D}}", td).replace("{{BEISPIEL_1}}", b1).replace("{{BEISPIEL_2}}", b2)
            .replace("{{ANNAHMEN}}", C.ASSUMPTIONS_MARKDOWN).replace("{{TESTS}}", anzahl))
    for name, wert in kennzahlen().items():
        text = text.replace("{{" + name + "}}", wert)
    (ROOT / "README.md").write_text(text, encoding="utf-8")
    print("README.md geschrieben")
