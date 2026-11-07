"""Erzeugt elr_precomputed.json: das Messraster (vier Verteilungen × Quaderzahlen 20, 40, 80 × 100 feste Instanzen × fünf Schlüssel × sechs Bedingungen: ohne und fünf Kombinationen aus Stopps und Anteil nicht
stapelbar), das CP-SAT-Orakel (n = 12, 40 Instanzen je Verteilung und Anteil nicht stapelbar) und die Stichprobe (die ersten Instanzen jeder Zelle einzeln, für die Tests).

    python generate_precomputed.py                         # rechnet alles neu (Orakel mit CP-SAT, Zeitlimit je Lauf, mehrere Prozesse)
    python generate_precomputed.py --keep-orakel           # behält das gespeicherte Orakel und rechnet Raster und Stichprobe neu
    python generate_precomputed.py --nur-stichprobe        # ergänzt in der vorhandenen Datei nur die Stichprobe
    python generate_precomputed.py --check                 # rechnet das Raster (parallel) nach und vergleicht mit der Datei (das Orakel nicht)

Das Orakel rechnet dev/opt.py (CP-SAT, ohne Stützbedingung) mit 3 Stopps; die Obergrenze ist die Behälterzahl der Heuristik (Schlüssel Grundfläche, ohne Stützbedingung) mit den Bedingungen."""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import elr_algorithm as A
import elr_constants as C
import elr_evaluation as ev
from elr_scenario import zufallsinstanz


def orakel_instanz(v: int, qi: int, j: int) -> tuple:
    """(Optimum ohne, Optimum mit Bedingungen, Heuristik ohne, Heuristik mit); -1 = nicht entschieden. Alles ohne Stützbedingung, 3 Stopps, Anteil nicht stapelbar C.ORAKEL_Q[qi]."""
    from dev.opt import optimum_cpsat

    inst = zufallsinstanz(v, C.ORAKEL_N, ev.orakel_seed(v, j))
    k, cap = inst.kisten, inst.cap
    stopp, stap = inst.stopps(C.ORAKEL_M), inst.stapelbar(C.ORAKEL_Q[qi])
    ein, alle = ev._neutral(inst.n)
    order = A.reihenfolge(k, stopp, C.GRUNDFLAECHE)
    h_ohne = len(A.pack(k, ein, alle, order, cap, 0.0)[0])
    h_mit = len(A.pack(k, stopp, stap, order, cap, 0.0)[0])
    ohne = optimum_cpsat(k, stopp, stap, cap, h_ohne, False, C.ORAKEL_ZEIT, 2)
    mit = optimum_cpsat(k, stopp, stap, cap, h_mit, True, C.ORAKEL_ZEIT, 2)
    return ohne, mit, h_ohne, h_mit


def _orakel_zelle(args):
    v, qi = args
    z = {"instanzen": C.ORAKEL_INSTANZEN, "entschieden": 0, "offen": 0, "ohne": 0, "mit": 0, "gleich": 0, "mehr": 0, "heur_ohne": 0, "heur_mit": 0, "trifft": 0}
    for j in range(C.ORAKEL_INSTANZEN):
        ohne, mit, h_ohne, h_mit = orakel_instanz(v, qi, j)
        if ohne < 0 or mit < 0:
            z["offen"] += 1
            continue
        z["entschieden"] += 1
        z["ohne"] += ohne
        z["mit"] += mit
        z["gleich" if mit == ohne else "mehr"] += 1
        z["heur_ohne"] += h_ohne
        z["heur_mit"] += h_mit
        z["trifft"] += h_mit == mit
    return f"{C.VERTEILUNGEN[v][0]}|{qi}", z


def _zelle(args):
    v, ni = args
    t = time.perf_counter()
    return v, ni, ev.messzelle(v, ni), time.perf_counter() - t


def _stichprobe_zelle(args):
    v, ni = args
    return ev.zelle_schluessel(v, ni), {str(j): ev.messzelle(v, ni, [j]) for j in C.STICHPROBE_J}


def _frisch(args):
    v, ni = args
    return ev.zelle_schluessel(v, ni), ev.messzelle(v, ni)


def _pool():
    return ProcessPoolExecutor(max(1, min(6, (os.cpu_count() or 2) // 2)))


def _zellen():
    return [(v, ni) for v in range(len(C.VERTEILUNGEN)) for ni in range(len(C.MESS_N))]


def stichprobe_ergaenzen(daten: dict) -> None:
    with _pool() as pool:
        daten["stichprobe"] = dict(pool.map(_stichprobe_zelle, _zellen()))


def erzeugen(behalten: bool) -> dict:
    daten = {"instanzen": C.INSTANZEN, "cap": C.CAP, "zellen": {}}
    if behalten:
        daten["orakel"] = ev.vorberechnet()["orakel"]
    else:
        with _pool() as pool:
            daten["orakel"] = dict(pool.map(_orakel_zelle, [(v, qi) for qi in range(len(C.ORAKEL_Q)) for v in range(len(C.VERTEILUNGEN))]))
        for k, z in daten["orakel"].items():
            print(f"Orakel {k}: {z['entschieden']} entschieden, {z['offen']} offen, gleich {z['gleich']}, mehr {z['mehr']}", flush=True)
    with _pool() as pool:
        for v, ni, z, sekunden in pool.map(_zelle, _zellen()):
            daten["zellen"][ev.zelle_schluessel(v, ni)] = z
            print(f"{ev.zelle_schluessel(v, ni)}: {sekunden:.0f} s", flush=True)
    daten["zellen"] = {ev.zelle_schluessel(v, ni): daten["zellen"][ev.zelle_schluessel(v, ni)] for v, ni in _zellen()}
    stichprobe_ergaenzen(daten)
    return daten


def schreiben(daten: dict) -> None:
    ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED.name)


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    schlecht = 0
    with _pool() as pool:
        for schl, frisch in pool.map(_frisch, _zellen()):
            if frisch != gespeichert["zellen"][schl]:
                schlecht += 1
                print("ABWEICHUNG", schl, flush=True)
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(pruefen())
    if "--nur-stichprobe" in sys.argv:
        d = json.loads(ev.PRECOMPUTED.read_text(encoding="utf-8"))
        stichprobe_ergaenzen(d)
        schreiben(d)
        sys.exit(0)
    schreiben(erzeugen("--keep-orakel" in sys.argv))
