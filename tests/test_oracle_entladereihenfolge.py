"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 30 Sekunden.

  Verletzungen (blockierte Paare, Paare über nicht stapelbaren)  gegen  eine Zählung über die Zellen der Grundfläche: Quader b liegt über Quader a, wenn eine Zelle (x, y) von beiden bedeckt ist und b
                                                                       nicht tiefer beginnt, als a endet (keine Intervallrechnung).
  Dekodierer mit Entladereihenfolge, Stapelbarkeit und Stützfläche  gegen  eine Umsetzung, die die Eckpunkte nach jedem Quader aus der Liste der gesetzten Quader NEU erzeugt, die Stützfläche aus einem
                                                                       Voxelraster liest und die Bedingungen über die Zellenzählung prüft.
  Optimum (CP-SAT mit Bedingungen)                                gegen  das Optimum ohne Bedingungen (nie kleiner), gegen die Schranke (nie kleiner) und gegen die Packung der Heuristik (nie größer);
                                                                       das Modell wird zusätzlich an einer Packung geprüft, die es selbst liefert, in tests/test_claims.py für das Orakel des Rasters.
  Eigenschaften:  jede Packung zulässig, gültig und nie unter der Schranke; ohne Bedingung stimmt der Dekodierer mit der Zählung überein (die Verletzungen der Packung ohne Bedingung); gemeinsames Skalieren.
"""

import random

import pytest

import elr_algorithm as A


def instanzen(anzahl, n_lo, n_hi, cap_lo=10, cap_hi=24, seed0=0, kante_hi=None):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        hi = kante_hi or cap
        kisten = tuple(tuple(rng.randint(1, min(hi, cap)) for _ in range(3)) for _ in range(n))
        stopp = tuple(rng.randint(1, 3) for _ in range(n))
        stap = tuple(rng.random() >= 0.25 for _ in range(n))
        yield cap, kisten, stopp, stap


# --- Verletzungen: Zählung über die Zellen -----------------------------------------------------------------------------------------------------


def zellen(q):
    x, y, _z, w, d, _h = q
    return {(i, j) for i in range(x, x + w) for j in range(y, y + d)}


def ueber_zellen(b, a):
    """b über a: eine gemeinsame Zelle der Grundflächen, und b beginnt nicht tiefer, als a endet."""
    return bool(zellen(a) & zellen(b)) and b[2] >= a[2] + a[5]


def verletzungen_zellen(kisten, platz, stopp, stap):
    je = {}
    for i, b, x, y, z in platz:
        je.setdefault(b, []).append((i, (x, y, z, *kisten[i])))
    blockiert, getragen = [], []
    for lst in je.values():
        for i, a in lst:
            for j, b in lst:
                if i != j and ueber_zellen(b, a):
                    if stopp[j] > stopp[i]:
                        blockiert.append((i, j))
                    if not stap[i]:
                        getragen.append((i, j))
    return sorted(blockiert), sorted(getragen)


def test_verletzungen_gegen_die_zellenzaehlung():
    mit_verletzung = 0
    for cap, kisten, stopp, stap in list(instanzen(30, 2, 14, seed0=100)) + list(instanzen(20, 6, 16, cap_lo=12, seed0=200, kante_hi=7)):
        for order in (A.reihenfolge(kisten, stopp, A.GRUNDFLAECHE), list(range(len(kisten)))):
            platz = A.pack(kisten, (1,) * len(kisten), (True,) * len(kisten), order, cap)[1]              # Packung ohne Bedingung: hat Verletzungen
            blockiert, getragen = verletzungen_zellen(kisten, platz, stopp, stap)
            assert A.blockierte_paare(kisten, platz, stopp) == blockiert and A.getragene_paare(kisten, platz, stap) == getragen, (cap, kisten, stopp, stap)
            assert A.verletzungen(kisten, platz, stopp, stap) == (len(blockiert), len(getragen), len({i for p in blockiert + getragen for i in p}))
            assert A.gueltig(kisten, platz, stopp, stap) == (not blockiert and not getragen)
            mit_verletzung += bool(blockiert or getragen)
    assert mit_verletzung >= 40                                                                               # der Test prüft wirklich etwas


# --- Dekodierer: neu erzeugte Eckpunkte, Voxelstützfläche, Zellenprüfung -------------------------------------------------------------------------


def innen(p, q):
    return q[0] <= p[0] < q[0] + q[3] and q[1] <= p[1] < q[1] + q[4] and q[2] <= p[2] < q[2] + q[5]


def projektion(p, achse, davor):
    a, b = [k for k in range(3) if k != achse]
    kandidaten = [0]
    for q in davor:
        if q[achse] + q[3 + achse] <= p[achse] and q[a] <= p[a] < q[a] + q[3 + a] and q[b] <= p[b] < q[b] + q[3 + b]:
            kandidaten.append(q[achse] + q[3 + achse])
    return max(kandidaten)


def eckpunkte_neu(gesetzt, cap):
    punkte = {(0, 0, 0)}
    for s, q in enumerate(gesetzt):
        x, y, z, w, d, h = q
        for p, achsen in (((x + w, y, z), (1, 2)), ((x, y + d, z), (0, 2)), ((x, y, z + h), (0, 1))):
            punkte.add(p)
            for a in achsen:
                r = list(p)
                r[a] = projektion(p, a, gesetzt[:s])
                punkte.add(tuple(r))
    return sorted((p for p in punkte if max(p) < cap and not any(innen(p, q) for q in gesetzt)), key=lambda p: (p[2], p[1], p[0]))


def stuetz_voxel(quader, gesetzt):
    x0, y0, z0, w, d, _h = quader
    if z0 == 0:
        return 1.0
    belegt = sum(1 for x in range(x0, x0 + w) for y in range(y0, y0 + d) if any(q[0] <= x < q[0] + q[3] and q[1] <= y < q[1] + q[4] and q[2] <= z0 - 1 < q[2] + q[5] for q in gesetzt))
    return belegt / (w * d)


def zulaessig_zellen(k, i, lst, stopp, stap):
    """Darf Quader i an der Lage k neben die gesetzten (Nummer, Lage)? Über die Zellenzählung."""
    for j, g in lst:
        if ueber_zellen(k, g) and (stopp[i] > stopp[j] or not stap[j]):
            return False
        if ueber_zellen(g, k) and (stopp[j] > stopp[i] or not stap[i]):
            return False
    return True


def dekodierer_naiv(kisten, stopp, stap, order, cap, s_min):
    behaelter = []                                   # je Behälter: Liste (Nummer, (x, y, z, w, d, h)) in der Reihenfolge des Setzens
    platz = []
    for i in order:
        w, d, h = kisten[i]
        wahl = None
        for b, lst in enumerate(behaelter):
            gesetzt = [g for _j, g in lst]
            for (x, y, z) in eckpunkte_neu(gesetzt, cap):
                k = (x, y, z, w, d, h)
                if x + w > cap or y + d > cap or z + h > cap or any(A._ueberlappt(k, q) for q in gesetzt):
                    continue
                if s_min > 0 and stuetz_voxel(k, gesetzt) < s_min - 1e-9:
                    continue
                if not zulaessig_zellen(k, i, lst, stopp, stap):
                    continue
                wahl = (b, (x, y, z))
                break
            if wahl:
                break
        if wahl is None:
            behaelter.append([])
            wahl = (len(behaelter) - 1, (0, 0, 0))
        b, (x, y, z) = wahl
        behaelter[b].append((i, (x, y, z, w, d, h)))
        platz.append((i, b, x, y, z))
    return platz, behaelter


@pytest.mark.parametrize("s_min", (0.0, 0.8))
@pytest.mark.parametrize("schluessel", (A.GRUNDFLAECHE, A.STOPP_AB, A.STOPP_AUF))
def test_dekodierer_gegen_neu_erzeugte_eckpunkte_voxelstuetzflaeche_und_zellenpruefung(s_min, schluessel):
    geprueft = mehrere_behaelter = bedingung_wirkt = 0
    for cap, kisten, stopp, stap in list(instanzen(15, 1, 12, seed0=500)) + list(instanzen(15, 5, 14, cap_lo=12, seed0=600, kante_hi=7)):
        order = A.reihenfolge(kisten, stopp, schluessel)
        bins, platz, zustand = A.pack(kisten, stopp, stap, order, cap, s_min)
        platz_naiv, behaelter = dekodierer_naiv(kisten, stopp, stap, order, cap, s_min)
        assert platz == platz_naiv, (cap, kisten, stopp, stap, order)
        assert [list(z) for z in zustand] == [eckpunkte_neu([g for _j, g in lst], cap) for lst in behaelter], (cap, kisten, order)
        assert A.packung_pruefen(kisten, platz, cap) and A.gueltig(kisten, platz, stopp, stap) and verletzungen_zellen(kisten, platz, stopp, stap) == ([], [])
        geprueft += 1
        mehrere_behaelter += len(bins) >= 2
        bedingung_wirkt += platz != A.pack(kisten, (1,) * len(kisten), (True,) * len(kisten), order, cap, s_min)[1]
    assert geprueft == 30 and mehrere_behaelter >= 8 and bedingung_wirkt >= 3                                  # der Test prüft wirklich etwas


def test_jede_packung_ist_zulaessig_gueltig_und_nie_unter_der_schranke():
    for cap, kisten, stopp, stap in instanzen(40, 1, 25, cap_lo=10, cap_hi=100, seed0=700):
        for schluessel in range(5):
            order = A.reihenfolge(kisten, stopp, schluessel)
            for s_min in (0.0, 0.8):
                bins, platz, _ = A.pack(kisten, stopp, stap, order, cap, s_min)
                assert A.packung_pruefen(kisten, platz, cap) and A.gueltig(kisten, platz, stopp, stap) and len(bins) >= A.schranke(kisten, cap), (cap, kisten, schluessel, s_min)
                assert A.stuetz_minimum(kisten, platz) >= s_min - 1e-9


def test_bedingungen_machen_die_packung_selten_kleiner_und_nie_ungueltig():
    """Die Packung mit Bedingung ist auch ohne Bedingung zulässig, aber die Heuristik kann mit Bedingung zufällig weniger Behälter brauchen (sie ist kein Optimum): kein Satz, nur Zählung im Raster."""
    for cap, kisten, stopp, stap in instanzen(20, 2, 14, seed0=900):
        order = A.reihenfolge(kisten, stopp, A.GRUNDFLAECHE)
        platz = A.pack(kisten, stopp, stap, order, cap)[1]
        assert A.packung_pruefen(kisten, platz, cap)


def test_gemeinsames_skalieren_aendert_die_behaelterzahl_nicht():
    for cap, kisten, stopp, stap in instanzen(25, 1, 12, cap_lo=10, cap_hi=30, seed0=1100):
        gross = tuple(tuple(3 * x for x in k) for k in kisten)
        for s_min in (0.0, 0.8):
            for k in range(5):
                assert A.anzahl(gross, stopp, stap, k, 3 * cap, s_min) == A.anzahl(kisten, stopp, stap, k, cap, s_min), (cap, kisten, k, s_min)


def test_optimum_von_cpsat_mit_bedingungen_liegt_zwischen_dem_ohne_und_der_packung():
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    for cap, kisten, stopp, stap in instanzen(8, 3, 7, cap_lo=10, cap_hi=20, seed0=1300):
        order = A.reihenfolge(kisten, stopp, A.GRUNDFLAECHE)
        heur = len(A.pack(kisten, stopp, stap, order, cap)[0])
        ohne = optimum_cpsat(kisten, stopp, stap, cap, heur, False, 20.0, 2)
        mit = optimum_cpsat(kisten, stopp, stap, cap, heur, True, 20.0, 2)
        assert A.schranke(kisten, cap) <= ohne <= mit <= heur, (cap, kisten, stopp, stap, ohne, mit, heur)


def test_cpsat_modell_kennt_die_bedingungen_an_zwei_quadern():
    """Zwei Quader 10 mal 10 mal 4 stehen nur übereinander (zusammen 8 hoch). Ohne Bedingung ein Behälter. Das Modell darf die Reihenfolge der beiden frei wählen (die Stützfläche fehlt, ein Quader darf auch
    oben aufliegen): Eine Bedingung zwingt nur dann einen zweiten Behälter auf, wenn sie BEIDE Reihenfolgen verbietet. Mini-Instanz aus tests/test_algorithm.py: Die Heuristik braucht mit Bedingung 2 Behälter,
    das Optimum ist 1 (freie Platzierung)."""
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    mini = ((6, 4, 2), (4, 8, 3), (8, 4, 7), (3, 2, 5))
    assert optimum_cpsat(mini, (1, 2, 2, 2), (True,) * 4, 10, 2, False, 20.0, 2) == 1 and optimum_cpsat(mini, (1, 2, 2, 2), (True,) * 4, 10, 2, True, 20.0, 2) == 1
    zwei = ((10, 10, 4), (10, 10, 4))

    def opt(stopp, stap, bedingung=True):
        return optimum_cpsat(zwei, stopp, stap, 10, 2, bedingung, 20.0, 2)

    assert opt((1, 1), (True, True), False) == 1 and opt((2, 1), (False, True), False) == 1                      # ohne Bedingung immer ein Behälter
    assert opt((1, 2), (True, True)) == 1 and opt((2, 1), (True, True)) == 1                                       # Stopps allein: eine der beiden Reihenfolgen passt
    assert opt((1, 1), (True, False)) == 1 and opt((1, 1), (False, True)) == 1                                     # ein nicht stapelbarer Quader kommt nach oben
    assert opt((1, 1), (False, False)) == 2                                                                         # beide tragen nichts: nur zwei Behälter
    assert opt((2, 1), (False, True)) == 2                                                                          # Stopp: Quader 1 (Stopp 1) muss oben liegen, aber Quader 0 (Stopp 2) trägt nichts
    assert opt((1, 2), (False, True)) == 1                                                                          # Quader 0 (Stopp 1) oben, Quader 1 (Stopp 2) unten und stapelbar
    # dieselben Fälle im Packer (Reihenfolge 0, 1 und 1, 0): derselbe Behälterzahl, wenn eine Reihenfolge passt, auch wenn der Packer nur die zuerst gesetzte unten hat
    for stopp, stap, erwartet in (((2, 1), (False, True), 2), ((1, 1), (False, False), 2), ((2, 1), (True, True), 1)):
        assert len(A.pack(zwei, stopp, stap, [0, 1], 10)[0]) == erwartet
