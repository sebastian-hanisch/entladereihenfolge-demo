"""Kern an der Mini-Instanz von Hand und an den Handbeispielen der App (DEMO-PLAYBOOK §1b).

Handrechnung Mini-Instanz (Behälter 10 mal 10 mal 10, keine Stützbedingung; Quader 0: (6,4,2) Stopp 1, 1: (4,8,3) Stopp 2, 2: (8,4,7) Stopp 2, 3: (3,2,5) Stopp 2; alle stapelbar; Reihenfolge 0, 1, 2, 3):
  Ohne Bedingung: Quader 0 -> (0,0,0); E = {(6,0,0), (0,4,0), (0,0,2)}. Quader 1 (x 6 bis 10, y 0 bis 8, z 0 bis 3) -> (6,0,0); neue Ecken (6,8,0), (6,0,3) und die Projektionen (0,8,0), (0,0,3)
  (die Ecke (6,0,3) gleitet in -x über Quader 0 hinweg, weil Quader 0 nur bis z = 2 reicht); (10,..) entfällt an der Wand; E = {(0,4,0), (0,8,0), (6,8,0), (0,0,2), (0,0,3), (6,0,3)}.
  Quader 2 (8,4,7): (0,4,0) überlappt Quader 1 (x 6 bis 8, y 4 bis 8, z 0 bis 3); (0,8,0) und (6,8,0) sind zu weit hinten (8 + 4 > 10); (0,0,2) überlappt Quader 1 (z 2 bis 3); (0,0,3) passt (z 3 bis 10).
  -> (0,0,3). Quader 3 (3,2,5): (0,4,0) passt (x 0 bis 3, y 4 bis 6, Quader 0 endet bei y = 4, Quader 2 liegt bei z >= 3 über y 0 bis 4). -> (0,4,0). Alles in einem Behälter.
  Über: Quader 2 beginnt bei z = 3 >= 0 + 2 (Oberseite von Quader 0) mit x 0 bis 8 und y 0 bis 4 über der Grundfläche von Quader 0 (x 0 bis 6, y 0 bis 4): 2 liegt über 0, und Stopp 2 > Stopp 1: ein blockiertes Paar
  (unten 0, oben 2). Quader 2 liegt auch über Quader 1 (z 3 >= 0 + 3, x 6 bis 8 gemeinsam), dort ist der Stopp gleich: erlaubt. Quader 3 liegt auf z = 0 und ist über niemandem.
  Mit Entladereihenfolge (Stopps 1, 2, 2, 2): Quader 2 an (0,0,3) wäre über Quader 0 mit Stopp 2 > 1: verboten. Die anderen Punkte sind zu klein oder überlappen: neuer Behälter, (0,0,0). Quader 3 geht in
  Behälter 0 an (0,4,0) (nicht über oder unter jemandem). -> [[0, 1, 3], [2]].
  Mit Stapelbarkeit (Quader 0 nicht stapelbar, alle Stopps 1): derselbe Ausgang, weil (0,0,3) über dem nicht stapelbaren Quader 0 läge.
Stützfläche von Quader 2 bei (0,0,3): Oberseite von Quader 1 bei z = 3, gemeinsame Fläche x 6 bis 8 mal y 0 bis 4 = 8 von 32 = 25 %; mit Mindest-Stützfläche 80 % wäre der Punkt ohnehin unzulässig.
"""

import pytest

import elr_algorithm as A
import elr_constants as C
from elr_scenario import beispiel

KISTEN = ((6, 4, 2), (4, 8, 3), (8, 4, 7), (3, 2, 5))
STOPP = (1, 2, 2, 2)
ALLE = (True, True, True, True)
EIN = (1, 1, 1, 1)


def test_reihenfolge_je_schluessel_mit_gleichstaenden_in_lieferreihenfolge():
    assert A.reihenfolge(KISTEN, STOPP, A.LIEFERUNG) == [0, 1, 2, 3]
    assert A.reihenfolge(KISTEN, STOPP, A.VOLUMEN) == [2, 1, 0, 3]                 # 224, 96, 48, 30
    assert A.reihenfolge(KISTEN, STOPP, A.GRUNDFLAECHE) == [1, 2, 0, 3]            # 32, 32 (Lieferreihenfolge), 24, 6
    assert A.reihenfolge(KISTEN, STOPP, A.STOPP_AB) == [1, 2, 3, 0]                # Stopp 2 zuerst (Grundfläche 32, 32, 6), dann Stopp 1
    assert A.reihenfolge(KISTEN, STOPP, A.STOPP_AUF) == [0, 1, 2, 3]               # Stopp 1 zuerst, dann Stopp 2 mit Grundfläche 32, 32, 6
    assert A.reihenfolge(KISTEN, EIN, A.STOPP_AB) == A.reihenfolge(KISTEN, EIN, A.GRUNDFLAECHE)       # ohne Stopps wie die Grundfläche


def test_ueber_von_hand():
    a = (0, 0, 0, 6, 4, 2)
    assert A.ueber((0, 0, 3, 8, 4, 7), a) and A.ueber((0, 0, 2, 3, 3, 3), a)                         # beginnt genau bei der Oberseite: darüber
    assert not A.ueber((0, 0, 1, 3, 3, 3), a)                                                         # beginnt tiefer, als a endet
    assert not A.ueber((6, 0, 2, 3, 3, 3), a) and not A.ueber((0, 4, 2, 3, 3, 3), a)                  # nur Berührung der Seiten: keine Überlappung der Grundflächen
    assert A.ueber((5, 3, 2, 3, 3, 3), a) and not A.ueber(a, (5, 3, 2, 3, 3, 3))                      # gemeinsame Fläche 1 mal 1: darüber, und nicht umgekehrt


def test_ohne_bedingung_auf_der_mini_instanz_mit_den_eckpunkten():
    bins, platz, zustand = A.pack(KISTEN, EIN, ALLE, [0, 1, 2, 3], 10)
    assert bins == [[0, 1, 2, 3]] and platz == [(0, 0, 0, 0, 0), (1, 0, 6, 0, 0), (2, 0, 0, 0, 3), (3, 0, 0, 4, 0)]
    assert A.pack(KISTEN, EIN, ALLE, [0], 10)[2] == [((6, 0, 0), (0, 4, 0), (0, 0, 2))]
    assert A.pack(KISTEN, EIN, ALLE, [0, 1], 10)[2] == [((0, 4, 0), (0, 8, 0), (6, 8, 0), (0, 0, 2), (0, 0, 3), (6, 0, 3))]
    assert A.blockierte_paare(KISTEN, platz, STOPP) == [(0, 2)]
    assert A.getragene_paare(KISTEN, platz, ALLE) == [] and A.verletzungen(KISTEN, platz, STOPP, ALLE) == (1, 0, 2)
    assert not A.gueltig(KISTEN, platz, STOPP, ALLE) and A.gueltig(KISTEN, platz, EIN, ALLE)


def test_mit_entladereihenfolge_braucht_quader_2_einen_neuen_behaelter():
    bins, platz, zustand = A.pack(KISTEN, STOPP, ALLE, [0, 1, 2, 3], 10)
    assert bins == [[0, 1, 3], [2]] and platz == [(0, 0, 0, 0, 0), (1, 0, 6, 0, 0), (2, 1, 0, 0, 0), (3, 0, 0, 4, 0)]
    assert A.gueltig(KISTEN, platz, STOPP, ALLE) and A.verletzungen(KISTEN, platz, STOPP, ALLE) == (0, 0, 0)


def test_mit_stapelbarkeit_allein_derselbe_ausgang():
    stap = (False, True, True, True)
    bins, platz, _ = A.pack(KISTEN, EIN, stap, [0, 1, 2, 3], 10)
    assert bins == [[0, 1, 3], [2]] and platz[2] == (2, 1, 0, 0, 0)
    _, ohne, _ = A.pack(KISTEN, EIN, ALLE, [0, 1, 2, 3], 10)
    assert A.getragene_paare(KISTEN, ohne, stap) == [(0, 2)] and A.blockierte_paare(KISTEN, ohne, EIN) == []
    assert A.verletzungen(KISTEN, ohne, EIN, stap) == (0, 1, 2)
    stap2 = (False, False, True, True)                                                                   # auch Quader 1 trägt nichts: Quader 2 läge über beiden
    assert A.getragene_paare(KISTEN, ohne, stap2) == [(0, 2), (1, 2)] and A.verletzungen(KISTEN, ohne, EIN, stap2) == (0, 2, 3)


def test_stuetzflaeche_von_quader_2_ohne_bedingung_ist_ein_viertel():
    _, platz, _ = A.pack(KISTEN, EIN, ALLE, [0, 1, 2, 3], 10)
    assert A.stuetzflaeche(KISTEN, platz, 2) == 8 / 32 and A.stuetz_minimum(KISTEN, platz) == 8 / 32
    mit = A.pack(KISTEN, EIN, ALLE, [0, 1, 2, 3], 10, 0.8)
    assert A.stuetz_minimum(KISTEN, mit[1]) >= 0.8 and mit[1][2][1] == 1                                    # mit Stützfläche 80 % ebenfalls ein neuer Behälter für Quader 2


def test_entladen_ab_und_entladene_quader(mini):
    _, platz, _ = A.pack(KISTEN, EIN, ALLE, [0, 1, 2, 3], 10)
    assert [p[0] for p in A.entladen_ab(platz, STOPP, 0)] == [0, 1, 2, 3]
    assert [p[0] for p in A.entladen_ab(platz, STOPP, 1)] == [1, 2, 3]
    assert A.entladen_ab(platz, STOPP, 2) == []
    assert mini.stopps(2) == STOPP and mini.stopps(1) == (1, 1, 1, 1) and mini.stapelbar(0.4) == (True,) * 4 and mini.stapelbar(0.6) == (False,) * 4


def test_anzahl_je_schluessel_der_mini_instanz_mit_und_ohne_bedingung():
    assert [A.anzahl(KISTEN, EIN, ALLE, k, 10) for k in range(5)] == [1, 1, 1, 1, 1]
    assert [A.anzahl(KISTEN, STOPP, ALLE, k, 10) for k in range(5)] == [2, 1, 1, 1, 2]            # Lieferung und Stopp auf packen in der Reihenfolge 0, 1, 2, 3 (von Hand: zwei Behälter)
    # Schlüssel Grundfläche (Reihenfolge 1, 2, 0, 3), von Hand: Quader 1 -> (0,0,0); Quader 2 -> (0,0,3) (über Quader 1, gleicher Stopp 2: erlaubt); Quader 0 (Stopp 1) -> (0,4,3) auf Quader 1
    # (y 4 bis 8, z 3 = Oberseite von Quader 1, über Quader 1 mit Stopp 1 <= 2) und neben Quader 2 (y 0 bis 4); Quader 3 -> (6,4,0): ein Behälter.
    assert A.pack(KISTEN, STOPP, ALLE, [1, 2, 0, 3], 10)[1] == [(1, 0, 0, 0, 0), (2, 0, 0, 0, 3), (0, 0, 0, 4, 3), (3, 0, 6, 4, 0)]
    # mit Stopp 1 zuerst (Stopp auf) wäre die Reihenfolge 0, 1, 2, 3: Quader 2 muss weg von Quader 0, weil er später entladen wird
    assert A.pack(KISTEN, STOPP, ALLE, A.reihenfolge(KISTEN, STOPP, A.STOPP_AUF), 10)[0] == [[0, 1, 3], [2]]


def test_schranken_der_mini_instanz():
    assert A.schranken(KISTEN, 10) == (1, 0, 1) and A.schranke(KISTEN, 10) == 1
    assert A.schranken(((6, 6, 6),) * 3, 10) == (1, 3, 3) and A.schranken(((10, 10, 10), (10, 10, 10), (1, 1, 1)), 10) == (3, 2, 3)


def test_packung_pruefen_erkennt_fehler():
    gut = [(0, 0, 0, 0, 0), (1, 0, 6, 0, 0), (2, 0, 0, 0, 3), (3, 0, 0, 4, 0)]
    assert A.packung_pruefen(KISTEN, gut, 10)
    assert not A.packung_pruefen(KISTEN, gut[:3], 10) and A.packung_pruefen(KISTEN, gut[:3], 10, vollstaendig=False)
    assert not A.packung_pruefen(KISTEN, gut + [(0, 1, 0, 0, 0)], 10)
    assert not A.packung_pruefen(KISTEN, [(0, 0, 0, 0, 0), (1, 0, 5, 0, 0), (2, 0, 0, 0, 3), (3, 0, 0, 4, 0)], 10)       # Quader 1 bei x = 5 überlappt Quader 0
    assert not A.packung_pruefen(KISTEN, [(0, 0, 0, 0, 0), (1, 0, 6, 0, 0), (2, 0, 0, 0, 4), (3, 0, 0, 4, 0)], 10)       # Quader 2 ragt über die Decke (4 + 7 > 10)
    assert A.packung_pruefen(KISTEN, [(0, 0, 0, 0, 0), (1, 0, 6, 0, 0), (2, 1, 0, 0, 0), (3, 0, 0, 4, 0)], 10)
    assert not A.packung_pruefen(KISTEN, [(9, 0, 0, 0, 0)], 10, vollstaendig=False)


def test_pack_lehnt_ungueltige_eingaben_ab():
    faelle = (((KISTEN, STOPP, ALLE, [0, 0], 10), {}), ((KISTEN, STOPP, ALLE, [4], 10), {}), ((((11, 3, 3),), (1,), (True,), [0], 10), {}), ((((0, 3, 3),), (1,), (True,), [0], 10), {}),
              ((((3, 3),), (1,), (True,), [0], 10), {}), ((KISTEN, STOPP, ALLE, [0], 10), {"s_min": 1.5}), ((KISTEN, (1, 2), ALLE, [0], 10), {}), ((KISTEN, STOPP, (True,), [0], 10), {}),
              ((KISTEN, (1, 2, 0, 2), ALLE, [0], 10), {}), ((KISTEN, (1, 2.5, 2, 2), ALLE, [0], 10), {}))
    for args, kw in faelle:
        with pytest.raises(ValueError):
            A.pack(*args, **kw)


def test_beispiele_der_app_mit_den_angaben_der_konstanten():
    """Die Behälterzahlen der beiden Handbeispiele aus dem Kommentar der Konstanten (3 Stopps, 20 % nicht stapelbar, Mindest-Stützfläche 80 %; Reihenfolge der Schlüssel: Lieferung, Volumen, Grundfläche, Stopp ab, Stopp auf)."""
    for b, erwartet in ((0, [2, 2, 1, 2, 2]), (1, [2, 2, 2, 2, 2])):
        inst = beispiel(b)
        stopp, stap = inst.stopps(3), inst.stapelbar(0.2)
        assert [A.anzahl(inst.kisten, stopp, stap, k, C.CAP, 0.8) for k in range(5)] == erwartet
        assert A.anzahl(inst.kisten, (1,) * 12, (True,) * 12, C.GRUNDFLAECHE, C.CAP, 0.8) == 1                    # ohne Bedingung bleibt die Grundfläche bei einem Behälter
    assert [A.schranke(beispiel(i).kisten, C.CAP) for i in (0, 1)] == [1, 1] and C.BEISPIEL_OPTIMUM == {0: 1, 1: 1}
