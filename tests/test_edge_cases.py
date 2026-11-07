"""Randfälle: leere Eingabe, ein Quader, Quader gleich Behälter, alle Stopps gleich, nur Stapelbarkeit, Gleichstände, Schritte, ungültige Eingaben, Grenzen der Regler."""

import pytest

import elr_algorithm as A
import elr_constants as C
import elr_evaluation as ev
from elr_scenario import Instance, mess_seed, zufallsinstanz


def test_leere_eingabe_ergibt_keine_behaelter():
    assert A.pack((), (), (), [], 10) == ([], [], [])
    assert A.schranken((), 10) == (0, 0, 0) and A.stuetz_minimum((), []) == 1.0
    assert A.verletzungen((), [], (), ()) == (0, 0, 0) and A.blockierte_paare((), [], ()) == [] and A.getragene_paare((), [], ()) == [] and A.gueltig((), [], (), ())
    assert A.entladen_ab([], (), 1) == []


@pytest.mark.parametrize("s_min", (0.0, 0.8))
def test_ein_quader_und_quader_gleich_behaelter(s_min):
    bins, platz, _ = A.pack(((7, 3, 5),), (3,), (False,), [0], 10, s_min)
    assert bins == [[0]] and platz == [(0, 0, 0, 0, 0)]
    bins, platz, _ = A.pack(((10, 10, 10), (1, 1, 1)), (1, 2), (False, True), [0, 1], 10, s_min)
    assert bins == [[0], [1]] and platz == [(0, 0, 0, 0, 0), (1, 1, 0, 0, 0)]


def test_nicht_stapelbarer_quader_traegt_nichts_auch_nicht_wenn_er_den_behaelter_fuellt():
    kisten = ((10, 10, 3), (4, 4, 4))
    bins, platz, _ = A.pack(kisten, (1, 1), (False, True), [0, 1], 10)
    assert bins == [[0], [1]]                                                      # der zweite Quader passt nur oben auf den ersten, der nichts trägt
    bins, platz, _ = A.pack(kisten, (1, 1), (True, True), [0, 1], 10)
    assert bins == [[0, 1]] and platz[1] == (1, 0, 0, 0, 3)


def test_der_zuerst_gesetzte_darf_unter_dem_spaeter_gesetzten_liegen_nur_wenn_die_stopps_passen():
    kisten = ((10, 10, 3), (4, 4, 4))
    assert A.pack(kisten, (1, 2), (True, True), [0, 1], 10)[0] == [[0], [1]]       # Quader 1 würde über Quader 0 liegen und später entladen: verboten
    assert A.pack(kisten, (2, 1), (True, True), [0, 1], 10)[0] == [[0, 1]]         # früher entladen oben: erlaubt
    assert A.pack(kisten, (2, 2), (True, True), [0, 1], 10)[0] == [[0, 1]]         # gleicher Stopp: erlaubt


def test_ein_quader_ueber_zwei_nachbarn_wird_gegen_beide_geprueft():
    # A und B stehen nebeneinander, C (breit genug für beide) kann nur über ihnen liegen; ob das geht, entscheiden die Stopps: C über A und B wird gegen beide geprüft.
    kisten = ((4, 10, 5), (4, 10, 5), (10, 4, 2))                                   # A und B stehen nebeneinander (x 0 bis 4 und 4 bis 8), C (10 breit, 4 tief, 2 hoch) liegt darüber bei z = 5
    stopp = (1, 1, 2)
    bins, platz, _ = A.pack(kisten, stopp, (True, True, True), [0, 1, 2], 10)
    assert bins == [[0, 1], [2]]                                                    # C (Stopp 2) würde über A und B (Stopp 1) liegen: verboten, neuer Behälter
    bins, platz, _ = A.pack(kisten, (2, 2, 1), (True, True, True), [0, 1, 2], 10)
    assert bins == [[0, 1, 2]] and platz[2][4] == 5                                 # C (Stopp 1) oben: erlaubt


def test_alle_stopps_gleich_und_alle_stapelbar_ist_ohne_bedingung(mini):
    for k in range(5):
        order = A.reihenfolge(mini.kisten, mini.stopps(1), k)
        assert A.pack(mini.kisten, mini.stopps(1), mini.stapelbar(0.0), order, 10) == A.pack(mini.kisten, (1,) * 4, (True,) * 4, order, 10)
        for s_min in (0.0, 0.8):
            assert A.anzahl(mini.kisten, mini.stopps(1), mini.stapelbar(0.0), k, 10, s_min) == A.anzahl(mini.kisten, (1,) * 4, (True,) * 4, k, 10, s_min)


def test_anfang_der_reihenfolge_ist_der_anfang_der_packung():
    inst = zufallsinstanz(1, 20, 3)
    stopp, stap = inst.stopps(3), inst.stapelbar(0.2)
    order = A.reihenfolge(inst.kisten, stopp, A.GRUNDFLAECHE)
    voll = A.pack(inst.kisten, stopp, stap, order, 100, 0.8)[1]
    for k in (0, 1, 7, 19, 20):
        assert A.pack(inst.kisten, stopp, stap, order[:k], 100, 0.8)[1] == voll[:k]


def test_gleichstaende_der_schluessel_bleiben_in_lieferreihenfolge():
    kisten = ((3, 3, 3), (3, 3, 3), (1, 1, 1), (3, 3, 3))
    for schluessel in (A.VOLUMEN, A.GRUNDFLAECHE):
        assert A.reihenfolge(kisten, (1, 1, 1, 1), schluessel) == [0, 1, 3, 2]
    assert A.reihenfolge(kisten, (2, 2, 1, 2), A.STOPP_AB) == [0, 1, 3, 2] and A.reihenfolge(kisten, (2, 2, 1, 2), A.STOPP_AUF) == [2, 0, 1, 3]


def test_ungueltige_instanzen_werden_abgelehnt():
    for kisten in (((0, 3, 3),), ((11, 3, 3),), ((3, 3),), ((3.5, 2, 2),), ((3, 3, 3, 3),)):
        with pytest.raises(ValueError):
            Instance(kisten, (0.5,), (0.5,), 10)
    for u, w in (((0.5, 0.5), (0.5,)), ((1.0,), (0.5,)), ((0.5,), (-0.1,))):
        with pytest.raises(ValueError):
            Instance(((1, 1, 1),), u, w, 10)
    with pytest.raises(ValueError):
        Instance(((1, 1, 1),), (0.5,), (0.5,), 0)
    leer = Instance(((1, 1, 1), (2, 2, 2)), (), (), 10)
    assert leer.stopps(5) == (1, 1) and leer.stapelbar(0.4) == (True, True)               # ohne Zufallszahlen: alle Stopps 1, alle stapelbar
    with pytest.raises(ValueError):
        leer.stopps(0)


def test_stopps_und_stapelbarkeit_aus_den_zufallszahlen():
    inst = Instance(((1, 1, 1),) * 4, (0.0, 0.34, 0.67, 0.999), (0.0, 0.19, 0.2, 0.5), 10)
    assert inst.stopps(1) == (1, 1, 1, 1) and inst.stopps(2) == (1, 1, 2, 2) and inst.stopps(3) == (1, 2, 3, 3) and inst.stopps(5) == (1, 2, 4, 5)
    assert inst.stapelbar(0.0) == (True,) * 4 and inst.stapelbar(0.2) == (False, False, True, True) and inst.stapelbar(0.4) == (False, False, False, True)       # w = 0,2 ist nicht kleiner als q = 0,2
    nested = [set(i for i, x in enumerate(inst.stapelbar(q)) if not x) for q in C.Q_WERTE]
    assert nested[0] <= nested[1] <= nested[2]


def test_analyse_an_den_grenzen_der_regler():
    for quelle in C.QUELLEN:
        for n_index in range(len(C.N_WERTE)):
            for seed in (0, C.SEED_MAX):
                for schritt, entladen in ((0, 0), (1, 1), (12, 5), (13, 2), (200, 3)):
                    a = ev.analyse(ev.Settings(quelle, n_index, seed, C.GRUNDFLAECHE, 3, 2, 1, 1, schritt, 50, 2, entladen))
                    assert A.packung_pruefen(a.inst.kisten, a.platz, a.inst.cap, vollstaendig=False)
                    assert 0 <= a.gezeigt < max(1, len(a.bins)) and 1 <= a.schritt <= a.inst.n and a.verletzung == (0, 0, 0) and a.stuetz_min >= 0.8 - 1e-9
    a = ev.analyse(ev.Settings(0, 0, 7, 1, 1, 0, 0, 1, 3, 1, 0, 0))
    assert a.schritt == 3 and len(a.platz) == 3
    assert ev.wirksamer_schritt(ev.Settings(schritt=0), 12) == 12 and ev.wirksamer_schritt(ev.Settings(schritt=13), 12) == 12 and ev.wirksamer_schritt(ev.Settings(schritt=-4), 12) == 12


def test_der_gezeigte_behaelter_wird_auf_den_letzten_begrenzt():
    a = ev.analyse(ev.Settings(1, 0, 7, C.LIEFERUNG, 2, 1, 1, 1, 0, 1, 1, 0))           # Beispiel 2, Lieferung, 3 Stopps, 20 % nicht stapelbar: zwei Behälter
    assert a.count == 2 and a.gezeigt == 0
    for wunsch, erwartet in ((2, 1), (3, 1), (50, 1)):
        assert ev.analyse(ev.Settings(1, 0, 7, C.LIEFERUNG, 2, 1, 1, 1, 0, wunsch, 1, 0)).gezeigt == erwartet
    assert ev.analyse(ev.Settings(1, 0, 7, C.LIEFERUNG, 2, 1, 1, 1, 2, 2, 1, 0)).gezeigt == 0                       # nach zwei Quadern gibt es nur einen Behälter


def test_entladen_nimmt_die_quader_der_ersten_stopps_aus_der_zeichnung():
    a0 = ev.analyse(ev.Settings(1, 0, 7, C.VOLUMEN, 2, 1, 1, 0, 0, 1, 1, 0))                                   # Bedingungen ignoriert, nichts entladen
    a1 = ev.analyse(ev.Settings(1, 0, 7, C.VOLUMEN, 2, 1, 1, 0, 0, 1, 1, 1))
    a3 = ev.analyse(ev.Settings(1, 0, 7, C.VOLUMEN, 2, 1, 1, 0, 0, 1, 1, 3))
    assert len(a0.platz) == 12 and len(a1.platz) == 12 - a1.entladen_zahl and a1.entladen_zahl == sum(1 for s in a1.stopp if s <= 1)
    assert a3.platz == () and a3.entladen_zahl == 12 and a0.entladen_zahl == 0 and a0.entladen_blockiert == 0
    assert all(a1.stopp[p[0]] > 1 for p in a1.platz)


def test_zufallsinstanzen_wachsen_mit_n_und_bleiben_im_bereich():
    for v, (_, _, bereiche) in enumerate(C.VERTEILUNGEN):
        for n in C.N_WERTE + C.MESS_N:
            inst = zufallsinstanz(v, n, mess_seed(v, 0, 5))
            assert inst.n == n and len(inst.u) == len(inst.w) == n and all(bereiche[a][0] <= k[a] <= bereiche[a][1] for k in inst.kisten for a in range(3))
            assert all(0 <= x < 1 for x in inst.u + inst.w) and max(inst.stopps(5)) <= 5 and min(inst.stopps(5)) >= 1


def test_zufallszahlen_sind_unabhaengig_von_den_massen_und_deterministisch():
    a, b = zufallsinstanz(0, 20, 123), zufallsinstanz(0, 20, 123)
    assert a == b and zufallsinstanz(0, 20, 124).u != a.u and zufallsinstanz(0, 20, 124).kisten != a.kisten


def test_mess_seeds_sind_verschieden():
    seeds = {mess_seed(v, ni, j) for v in range(4) for ni in range(3) for j in range(C.INSTANZEN)}
    assert len(seeds) == 4 * 3 * C.INSTANZEN
