"""Kennzahlen, Verdikt-Logik und das Messraster (vorberechnet in elr_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import elr_algorithm as A
import elr_constants as C
from elr_scenario import Instance, mess_seed, quelle_instanz, zufallsinstanz

PRECOMPUTED = Path(__file__).resolve().parent / "elr_precomputed.json"
SCHLUESSEL_LISTE = tuple(sorted(C.SCHLUESSEL))
BEDINGUNG_LISTE = tuple(sorted(C.BEDINGUNGEN))
GRUNDFLAECHE, STOPP_AB, STOPP_AUF = C.GRUNDFLAECHE, C.STOPP_AB, C.STOPP_AUF


@dataclass(frozen=True)
class Settings:
    quelle: int = 0
    n_index: int = 0
    seed: int = C.DEFAULT_SEED
    schluessel: int = GRUNDFLAECHE
    m_index: int = 2            # Index in C.M_WERTE: Zahl der Stopps (3)
    q_index: int = 1            # Index in C.Q_WERTE: Anteil nicht stapelbar (20 %)
    s_index: int = 1            # Index in C.S_WERTE: Mindest-Stützfläche (80 %)
    anwenden: int = 1           # 1 = der Packer beachtet Entladereihenfolge und Stapelbarkeit, 0 = er ignoriert sie (die Verletzungen werden trotzdem gezählt)
    schritt: int = 0            # 0 = alle Quader, sonst der Zwischenstand nach so vielen Quadern
    behaelter: int = 1          # welcher Behälter gezeichnet wird (1 = erster); größere Werte zeigen den letzten
    farbe: int = 1              # 0 Reihenfolge des Setzens, 1 Stopp, 2 Stapelbarkeit
    entladen: int = 0           # 0 = alles im Fahrzeug, sonst sind die Stopps 1 bis `entladen` entladen (die Quader sind aus der Zeichnung)


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    stopp: tuple          # Stopp je Quader (bei m Stopps)
    stapelbar: tuple      # Stapelbarkeit je Quader (beim Anteil q)
    order: tuple          # alle Quadernummern in der Reihenfolge, in der gepackt wird
    schritt: int          # Zahl der gesetzten Quader im gezeigten Zustand
    bins: tuple           # Behälter (Quadernummern) im gezeigten Zustand
    platz: tuple          # Platzierungen im gezeigten Zustand (nach dem Entladen: nur die Quader, die noch da sind)
    zustand: tuple        # Eckpunkte je Behälter im gezeigten Zustand
    gezeigt: int          # Nummer (ab 0) des gezeichneten Behälters im gezeigten Zustand
    count: int            # Behälterzahl der ganzen Packung
    ohne: int             # Behälterzahl ohne Entladereihenfolge und Stapelbarkeit (also ohne Stopps) bei gleichem Schlüssel und gleicher Mindest-Stützfläche
    schranke: int
    opt: object           # Optimum (int, CP-SAT, ohne Stützbedingung) bei den Handbeispielen, sonst None
    tabelle: tuple        # tabelle[schluessel][bedingung] = Behälterzahl, 5 x 4 (ohne Bedingung, nur Entladereihenfolge, nur Stapelbarkeit, beide)
    verletzung: tuple     # (blockierte Paare, Paare über nicht stapelbaren, betroffene Quader) der ganzen Packung
    verletzung_ohne: tuple  # dieselben Zahlen für die Packung ohne Bedingung (gleicher Schlüssel und gleiche Mindest-Stützfläche), gemessen an den Stopps und der Stapelbarkeit dieser Instanz
    entladen_blockiert: int  # Zahl der Quader mit Stopp bis `entladen`, die in der ganzen Packung unter einem später zu entladenden Quader liegen (0 bei angewendeter Bedingung)
    entladen_zahl: int    # Zahl der Quader, die bis zum Stopp `entladen` entladen sind
    stuetz_min: float     # kleinste Stützfläche aller Quader der ganzen Packung
    settings: Settings


def m_wert(s: Settings) -> int:
    return C.M_WERTE[s.m_index]


def q_wert(s: Settings) -> float:
    return C.Q_WERTE[s.q_index]


def s_min(s: Settings) -> float:
    return C.S_WERTE[s.s_index]


def _neutral(n: int):
    return (1,) * n, (True,) * n


def tabelle(inst: Instance, m: int, q: float, smin: float) -> tuple:
    """Behälterzahl für jede Kombination aus Schlüssel (Zeile) und Bedingung (Spalte: ohne, nur Entladereihenfolge, nur Stapelbarkeit, beide) bei m Stopps und dem Anteil q nicht stapelbar.
    Stopps gibt es nur, wenn die Entladereihenfolge gilt: In den Spalten ohne Entladereihenfolge (ohne Bedingung, nur Stapelbarkeit) sind alle Stopps 1, und die Schlüssel Stopp ab und Stopp auf sortieren dort
    wie die Grundfläche."""
    n = inst.n
    stopp, stap = inst.stopps(m), inst.stapelbar(q)
    ein, alle = _neutral(n)
    spalten = ((ein, alle, ein), (stopp, alle, stopp), (ein, stap, ein), (stopp, stap, stopp))      # (Stopps der Bedingung, Stapelbarkeit, Stopps für den Schlüssel)
    return tuple(tuple(len(A.pack(inst.kisten, s, st, A.reihenfolge(inst.kisten, so, k), inst.cap, smin)[0]) for s, st, so in spalten) for k in SCHLUESSEL_LISTE)


def wirksamer_schritt(settings: Settings, n: int) -> int:
    """Zahl der gezeigten Schritte: 0 oder mehr als n bedeutet alle Quader."""
    return n if settings.schritt <= 0 or settings.schritt > n else settings.schritt


def analyse(s: Settings) -> Analysis:
    inst = quelle_instanz(s.quelle, C.N_WERTE[s.n_index], s.seed)
    n = inst.n
    stopp, stap = inst.stopps(m_wert(s)), inst.stapelbar(q_wert(s))
    ein, alle = _neutral(n)
    pstopp, pstap = (stopp, stap) if s.anwenden else (ein, alle)
    smin = s_min(s)
    order = A.reihenfolge(inst.kisten, stopp, s.schluessel)
    schritt = wirksamer_schritt(s, n)
    bins_voll, platz_voll, _ = A.pack(inst.kisten, pstopp, pstap, order, inst.cap, smin)
    assert A.packung_pruefen(inst.kisten, platz_voll, inst.cap)
    assert A.stuetz_minimum(inst.kisten, platz_voll) >= smin - 1e-9
    if s.anwenden:
        assert A.gueltig(inst.kisten, platz_voll, stopp, stap)
    bins, platz0, zustand = A.pack(inst.kisten, pstopp, pstap, order[:schritt], inst.cap, smin)
    assert A.packung_pruefen(inst.kisten, platz0, inst.cap, vollstaendig=False)
    ohne_bins, ohne_platz, _ = A.pack(inst.kisten, ein, alle, A.reihenfolge(inst.kisten, ein, s.schluessel), inst.cap, smin)
    platz = A.entladen_ab(platz0, stopp, s.entladen) if s.entladen else list(platz0)
    gezeigt = max(0, min(s.behaelter, len(bins)) - 1)
    blockiert_unten = {i for i, _j in A.blockierte_paare(inst.kisten, platz_voll, stopp)}
    entladen_blockiert = sum(1 for i in blockiert_unten if stopp[i] <= s.entladen) if s.entladen else 0
    entladen_zahl = sum(1 for i in range(n) if stopp[i] <= s.entladen) if s.entladen else 0
    return Analysis(inst, stopp, stap, tuple(order), schritt, tuple(tuple(b) for b in bins), tuple(platz), tuple(zustand), gezeigt, len(bins_voll), len(ohne_bins), A.schranke(inst.kisten, inst.cap),
                    C.BEISPIEL_OPTIMUM.get(s.quelle), tabelle(inst, m_wert(s), q_wert(s), smin), A.verletzungen(inst.kisten, platz_voll, stopp, stap), A.verletzungen(inst.kisten, ohne_platz, stopp, stap),
                    entladen_blockiert, entladen_zahl, A.stuetz_minimum(inst.kisten, platz_voll), s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def beste_schluessel(tab: tuple, spalte: int) -> list:
    """Schlüssel mit der kleinsten Behälterzahl in der Spalte der Bedingung."""
    werte = [tab[k][spalte] for k in SCHLUESSEL_LISTE]
    return [k for k in SCHLUESSEL_LISTE if tab[k][spalte] == min(werte)]


def _namen(schluessel: list) -> str:
    return " oder ".join(C.SCHLUESSEL_KURZ[k] for k in schluessel)


def bedingungstext(s: Settings) -> str:
    m, q = m_wert(s), q_wert(s)
    teile = []
    if m > 1:
        teile.append(f"{m} Stopps")
    if q > 0:
        teile.append(f"{round(100 * q)} % nicht stapelbar")
    return " und ".join(teile) if teile else "keine Entlade- und Stapelbedingung"


def verdict_aktuell(a: Analysis) -> tuple[str, str]:
    """Verdikt zur gewählten Kombination: Behälterzahl der ganzen Packung gegen die Behälterzahl ohne Entladereihenfolge und Stapelbarkeit (gleicher Schlüssel), gegen das Optimum und gegen den besten Schlüssel."""
    s = a.settings
    schluessel = C.SCHLUESSEL_MIT[s.schluessel]
    if a.opt is None:
        opt_teil = f" Ein Optimum ist für diese Instanz nicht berechnet; die Schranke ist {a.schranke}."
    elif a.count == a.opt:
        opt_teil = f" Das ist das Optimum ohne Stützbedingung (die Schranke allein ergäbe {a.schranke})."
    else:
        opt_teil = f" Das Optimum ohne Stützbedingung ist **{a.opt}** (die Schranke ist {a.schranke})."
    if not s.anwenden:
        return "info", f"Nach {schluessel} sortiert und ohne Beachtung der Bedingungen brauchen die Quader **{a.count}** Behälter." + opt_teil + " Die Verletzungen stehen im Abschnitt unten."
    kopf = f"Nach {schluessel} sortiert und mit {bedingungstext(s)} gesetzt brauchen die Quader **{a.count}** Behälter, ohne Bedingung {a.ohne}."
    beste = beste_schluessel(a.tabelle, 3)
    passt = " Für beide Bedingungen ist das einer der besten Schlüssel dieser Instanz." if s.schluessel in beste else f" Für beide Bedingungen ist in der Tabelle {_namen(beste)} besser ({a.tabelle[beste[0]][3]})."
    if a.count > a.ohne:
        return "warning", kopf + f" Die Bedingungen kosten hier {a.count - a.ohne}." + opt_teil + passt
    if a.count < a.ohne:
        return "success", kopf + f" Die Bedingungen sparen hier {a.ohne - a.count} (die Platzierung der Quader ändert sich)." + opt_teil + passt
    return "info", kopf + " Die Bedingungen kosten hier nichts." + opt_teil + passt


def verdict_tabelle(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Hilft es, nach dem Stopp zu sortieren? Verglichen werden in der Spalte „beide Bedingungen“ der Schlüssel Stopp ab, die Gegenprobe Stopp auf und die Grundfläche (derselbe Schlüssel ohne Stopp)."""
    t = a.tabelle
    ab, auf, gr = t[STOPP_AB][3], t[STOPP_AUF][3], t[GRUNDFLAECHE][3]
    teil = f"Mit beiden Bedingungen braucht {C.SCHLUESSEL_KURZ[STOPP_AB]} **{ab}** Behälter, {C.SCHLUESSEL_KURZ[STOPP_AUF]} (Gegenprobe) {auf}, die Grundfläche ohne Rücksicht auf den Stopp {gr}."
    if ab < gr:
        return "success", teil + " Hier hilft es, nach dem Stopp zu sortieren."
    if ab == gr:
        return "info", teil + " Hier bringt das Sortieren nach dem Stopp nichts."
    return "warning", teil + " Hier **schadet** das Sortieren nach dem Stopp."


def verdict_verletzung(a: Analysis) -> tuple[str, str]:
    """Verdikt zur Packung OHNE Bedingung (gleicher Schlüssel und gleiche Mindest-Stützfläche): wie viele Paare blockieren, wie viele Quader liegen über nicht stapelbaren, wie viele Quader sind betroffen?"""
    blockiert, getragen, betroffen = a.verletzung_ohne
    n = a.inst.n
    if blockiert == 0 and getragen == 0:
        return "success", f"In der Packung ohne Bedingung gibt es hier weder blockierte Paare noch Quader über nicht stapelbaren (die Bedingungen kosten dann nichts)."
    teil = (f"In der Packung ohne Bedingung blockieren **{blockiert}** Paare (ein später zu entladender Quader liegt über einem früheren), und {getragen} Paare liegen über nicht stapelbaren Quadern; "
            f"**{betroffen}** von {n} Quadern sind betroffen.")
    return "warning", teil + " Solche Packungen müssten beim Entladen umgestaut werden."


def verdict_entladen(a: Analysis) -> tuple[str, str]:
    """Verdikt zum Entladen bis zum Stopp k: Wie viele Quader sind entladen, und wie viele davon lagen unter einem später zu entladenden Quader (müssten umgestaut werden)?"""
    s = a.settings
    if s.entladen == 0:
        return "info", "Wählen Sie „Entladen bis Stopp“, um die Quader der ersten Stopps aus dem Fahrzeug zu nehmen."
    teil = f"Nach dem Entladen der Stopps 1 bis {s.entladen} sind **{a.entladen_zahl}** von {a.inst.n} Quadern entladen."
    if a.entladen_blockiert == 0:
        return "success", teil + " Keiner davon lag unter einem Quader, der später entladen wird: Alle waren von oben frei."
    return "warning", teil + f" **{a.entladen_blockiert}** davon lagen unter einem später zu entladenden Quader und müssten umgestaut werden."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Messraster


def messzelle(verteilung: int, n_index: int, instanzen=None) -> dict:
    """Rechnet eine Zelle des Messrasters frisch: Summen (ganze Zahlen) über INSTANZEN feste Instanzen (oder nur über die Nummern `instanzen`, so rechnen die Tests Stichproben nach).

    ueber_schranke[k][c]: Summe von (Behälter mit Schlüssel k und der Kombination c minus Schranke); c = "0" ohne Bedingung (alle Stopps 1, alle stapelbar), c = "1" bis "5" die Kombinationen aus C.KOMBIS
    (Zahl der Stopps, Anteil nicht stapelbar), jeweils mit beiden Bedingungen. mehr_als_ohne[k][c] (c ab 1): Zahl der Instanzen mit mehr Behältern als ohne Bedingung. verletzung[c] (c ab 1): Summen für
    die Packung OHNE Bedingung mit dem Schlüssel Grundfläche, gemessen an den Stopps und der Stapelbarkeit der Kombination c: blockierte Paare, Paare über nicht stapelbaren, betroffene Quader. Immer
    gilt die Mindest-Stützfläche C.MESS_SMIN."""
    n = C.MESS_N[n_index]
    ks = [str(k) for k in SCHLUESSEL_LISTE]
    cs = [str(c) for c in range(len(C.KOMBIS) + 1)]
    out = {"ueber_schranke": {k: dict.fromkeys(cs, 0) for k in ks}, "mehr_als_ohne": {k: dict.fromkeys(cs[1:], 0) for k in ks},
           "verletzung": {c: {"paare": 0, "nicht": 0, "quader": 0} for c in cs[1:]}}
    for j in (range(C.INSTANZEN) if instanzen is None else instanzen):
        inst = zufallsinstanz(verteilung, n, mess_seed(verteilung, n_index, j))
        kisten, cap = inst.kisten, inst.cap
        s = A.schranke(kisten, cap)
        ein, alle = _neutral(n)
        kombis = [(inst.stopps(m), inst.stapelbar(q)) for m, q in C.KOMBIS]
        for k in SCHLUESSEL_LISTE:
            basis = None
            for c in range(len(C.KOMBIS) + 1):
                if c == 0:
                    zahl = A.anzahl(kisten, ein, alle, k, cap, C.MESS_SMIN)
                    basis = zahl
                else:
                    stopp, stap = kombis[c - 1]
                    order = A.reihenfolge(kisten, stopp, k)
                    zahl = len(A.pack(kisten, stopp, stap, order, cap, C.MESS_SMIN)[0])
                    out["mehr_als_ohne"][str(k)][str(c)] += zahl > basis
                out["ueber_schranke"][str(k)][str(c)] += zahl - s
        for c in range(1, len(C.KOMBIS) + 1):
            stopp, stap = kombis[c - 1]
            order = A.reihenfolge(kisten, stopp, C.VERLETZUNGS_SCHLUESSEL)
            platz = A.pack(kisten, ein, alle, order, cap, C.MESS_SMIN)[1]
            p, nn, q = A.verletzungen(kisten, platz, stopp, stap)
            r = out["verletzung"][str(c)]
            r["paare"] += p
            r["nicht"] += nn
            r["quader"] += q
    return out


def orakel_seed(verteilung: int, j: int) -> int:
    """Seed der j-ten Instanz des CP-SAT-Orakels (eigene Instanzen, nicht aus dem Raster)."""
    return 8_000_000 + 100_000 * verteilung + j


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(verteilung: int, n_index: int) -> str:
    return f"{C.VERTEILUNGEN[verteilung][0]}|{C.MESS_N[n_index]}"


def zeile(verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    """Mittelwerte und Anteile einer Zelle aus den vorberechneten Summen."""
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(verteilung, n_index)]
    k = daten["instanzen"]
    n = C.MESS_N[n_index]
    cs = range(len(C.KOMBIS) + 1)
    return {
        "verteilung": verteilung,
        "name": C.VERTEILUNG_LANG[verteilung],
        "n": n,
        "instanzen": k,
        "mittel": {s_k: {c: z["ueber_schranke"][str(s_k)][str(c)] / k for c in cs} for s_k in SCHLUESSEL_LISTE},
        "mehr": {s_k: {c: z["mehr_als_ohne"][str(s_k)][str(c)] for c in cs if c > 0} for s_k in SCHLUESSEL_LISTE},
        "verletzung": {c: {"paare": z["verletzung"][str(c)]["paare"] / k, "nicht": z["verletzung"][str(c)]["nicht"] / k, "quader": 100.0 * z["verletzung"][str(c)]["quader"] / (n * k)} for c in cs if c > 0},
    }


def gerundet(m: dict) -> dict:
    return {k: {c: round(m[k][c], 2) for c in m[k]} for k in m}


def beste_schluessel_zelle(g: dict, c: int) -> list:
    """Schlüssel mit dem kleinsten (auf zwei Stellen gerundeten) Mittel bei der Kombination c."""
    kleinster = min(g[k][c] for k in SCHLUESSEL_LISTE)
    return [k for k in SCHLUESSEL_LISTE if g[k][c] == kleinster]


def verdict_kosten(z: dict) -> tuple[str, str]:
    """Experiment 1: Kosten der Bedingungen in der gewählten Zelle für die Grundfläche (Mittel der Behälter über der Schranke, auf zwei Stellen gerundet): ohne Bedingung, drei Stopps, drei Stopps und 40 % nicht stapelbar."""
    g = gerundet(z["mittel"])
    a, b, c = g[GRUNDFLAECHE][0], g[GRUNDFLAECHE][2], g[GRUNDFLAECHE][5]
    teil = (f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} braucht die Grundfläche über der Schranke ohne Bedingung {a:.2f} Behälter, mit 3 Stopps {b:.2f} und mit 3 Stopps und 40 % nicht stapelbar {c:.2f} "
            f"({z['instanzen']} Instanzen).")
    if c > a:
        return "warning", teil + f" Die Bedingungen kosten bis zu {c - a:.2f} Behälter im Mittel."
    return "info", teil + " Die Bedingungen kosten in dieser Zelle nichts."


def verdict_messung(z: dict) -> tuple[str, str]:
    """Experiment 2: der beste Schlüssel je Kombination (Mittel, auf zwei Stellen gerundet); schlägt der Schlüssel Stopp ab die Grundfläche?"""
    g = gerundet(z["mittel"])
    teile = []
    for c in range(len(C.KOMBIS) + 1):
        beste = beste_schluessel_zelle(g, c)
        name = "ohne Bedingung" if c == 0 else C.KOMBI_KURZ[c - 1]
        teile.append(f"{name} {'alle gleich' if len(beste) == len(SCHLUESSEL_LISTE) else ' und '.join(C.SCHLUESSEL_KURZ[k] for k in beste)}")
    kopf = f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} ist der beste Schlüssel je Bedingung (Mittel über {z['instanzen']} Instanzen): " + "; ".join(teile) + "."
    besser = [c for c in range(1, len(C.KOMBIS) + 1) if g[STOPP_AB][c] < g[GRUNDFLAECHE][c]]
    if besser:
        return "success", kopf + f" Der Schlüssel Stopp ab schlägt die Grundfläche bei {', '.join(C.KOMBI_KURZ[c - 1] for c in besser)}."
    return "info", kopf + " Der Schlüssel Stopp ab schlägt die Grundfläche in keiner Kombination: Vermutlich erzwingt der Packer die Bedingung ohnehin (nicht getestet), das Sortieren nach dem Stopp bringt hier nichts."


def verdict_verletzung_raster(z: dict) -> tuple[str, str]:
    """Experiment 3: Anteil der betroffenen Quader in der Packung ohne Bedingung bei 2, 3 und 5 Stopps (ohne nicht stapelbare), auf ganze Prozent gerundet."""
    v = z["verletzung"]
    a, b, c = round(v[1]["quader"]), round(v[2]["quader"]), round(v[3]["quader"])
    teil = (f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} sind in der Packung ohne Bedingung bei 2 Stopps {a} %, bei 3 Stopps {b} % und bei 5 Stopps {c} % der Quader von einer Blockierung betroffen "
            f"(im Mittel {v[2]['paare']:.1f} blockierte Paare bei 3 Stopps).")
    return "warning", teil + " Je mehr Stopps, desto mehr Quader müssten beim Entladen umgestaut werden."


def orakel_zeilen(daten: dict | None = None) -> list:
    """Experiment 4: je Verteilung und Anteil nicht stapelbar (3 Stopps, n = 12) das Optimum ohne und mit Bedingungen (CP-SAT, ohne Stützbedingung) und die Heuristik (Schlüssel Grundfläche, ohne Stützbedingung)."""
    daten = daten or vorberechnet()
    zeilen = []
    for qi, q in enumerate(C.ORAKEL_Q):
        for v, (name, *_x) in enumerate(C.VERTEILUNGEN):
            z = daten["orakel"][f"{name}|{qi}"]
            e = z["entschieden"]
            zeilen.append({"verteilung": v, "q": q, "instanzen": z["instanzen"], "entschieden": e, "offen": z["offen"], "ohne": z["ohne"] / e if e else None, "mit": z["mit"] / e if e else None,
                           "gleich": z["gleich"], "mehr": z["mehr"], "heur_ohne": z["heur_ohne"] / e if e else None, "heur_mit": z["heur_mit"] / e if e else None, "trifft": z["trifft"]})
    return zeilen


def verdict_orakel(zeilen: list) -> tuple[str, str]:
    """Verdikt zu Experiment 4: Wie viel kosten die Bedingungen im Optimum, wie viel in der Heuristik (Mittel über die entschiedenen Instanzen aller Zeilen mit dem Anteil q = 0 beziehungsweise q = 40 %)?"""
    def mittel(sel, feld):
        zs = [z for z in sel if z["entschieden"]]
        return sum(z[feld] * z["entschieden"] for z in zs) / sum(z["entschieden"] for z in zs)

    nur = [z for z in zeilen if z["q"] == 0.0]
    viel = [z for z in zeilen if z["q"] == max(C.ORAKEL_Q)]
    opt_nur = round(mittel(nur, "mit") - mittel(nur, "ohne"), 2)
    opt_viel = round(mittel(viel, "mit") - mittel(viel, "ohne"), 2)
    heur_nur = round(mittel(nur, "heur_mit") - mittel(nur, "heur_ohne"), 2)
    heur_viel = round(mittel(viel, "heur_mit") - mittel(viel, "heur_ohne"), 2)
    teil = (f"Im Optimum kostet die Entladereihenfolge allein bei 3 Stopps im Mittel {opt_nur:+.2f} Behälter, mit 40 % nicht stapelbar {opt_viel:+.2f}; in der Heuristik sind es {heur_nur:+.2f} beziehungsweise {heur_viel:+.2f} "
            "(Mittel über die vier Verteilungen, n = 12, ohne Stützbedingung).")
    if heur_viel > opt_viel:
        return "info", teil + " Die Heuristik zahlt mehr für die Bedingungen, als die Aufgabe verlangt."
    return "info", teil + " Die Heuristik zahlt nicht mehr als das Optimum."
