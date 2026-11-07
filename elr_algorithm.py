"""Kern der Demo (nur Standardbibliothek): Schlüssel, Extreme Points mit Projektionen unter Mindest-Stützfläche, Entladereihenfolge und Stapelbarkeit, die Prüfer und die Kennzahlen der Verletzungen.

Quader (Breite, Tiefe, Höhe), ohne Drehung, in Behälter der Kantenlänge `cap`. Jeder Quader hat einen **Stopp** (1 = wird zuerst entladen) und ist stapelbar oder nicht. Jeder Quader kommt in den ersten
Behälter, in dem ein Eckpunkt ihn aufnimmt (Stück 9), und dort an den zulässigen Eckpunkt mit kleinstem (z, y, x). Eine Packung ist eine Liste (Quader, Behälter, x, y, z).

Zwei Bedingungen kommen zu Stück 9 und 10 hinzu, beide nur auf den Quadern **desselben Behälters**:
  * **Entladereihenfolge:** Quader B liegt ÜBER Quader A, wenn sich ihre Grundflächen mit einer Fläche über null überlappen und B nicht tiefer beginnt als A endet (z_B >= z_A + h_A). Ist B über A, muss
    Stopp(B) <= Stopp(A) sein: Was über einem anderen liegt, wird nicht später entladen als das, was darunter liegt, sonst müsste B vor A weggeräumt werden. Geprüft wird nur diese Blockierung von OBEN;
    die seitliche Zufahrt zur Tür (hinten und vorn, links und rechts) wird nicht geprüft.
  * **Stapelbarkeit:** Ein nicht stapelbarer Quader trägt nichts: Es gibt keinen Quader über ihm (also auch keinen, der nur darüber schwebt oder auf anderen aufliegt)."""

LIEFERUNG, VOLUMEN, GRUNDFLAECHE, STOPP_AB, STOPP_AUF = 0, 1, 2, 3, 4
EPS = 1e-9


# --- Schlüssel --------------------------------------------------------------------------------------------------------------------------------------


def reihenfolge(kisten, stopp, schluessel: int) -> list:
    """Quadernummern in der Reihenfolge, in der gepackt wird. 0 Lieferung; 1 Volumen fallend; 2 Grundfläche fallend; 3 Stopp fallend, dann Grundfläche fallend (der Quader, der zuletzt entladen wird, kommt
    zuerst nach unten); 4 Stopp aufsteigend, dann Grundfläche fallend (Gegenprobe: das Falsche zuerst). Gleichstände bleiben in der Lieferreihenfolge."""
    n = len(kisten)
    vol = [w * d * h for w, d, h in kisten]
    gr = [w * d for w, d, _h in kisten]
    schluessel_funktion = {LIEFERUNG: lambda i: (i,), VOLUMEN: lambda i: (-vol[i], i), GRUNDFLAECHE: lambda i: (-gr[i], i), STOPP_AB: lambda i: (-stopp[i], -gr[i], i),
                           STOPP_AUF: lambda i: (stopp[i], -gr[i], i)}
    return sorted(range(n), key=schluessel_funktion[schluessel])


# --- Geometrie --------------------------------------------------------------------------------------------------------------------------------------


def _ueberlappt(a, b) -> bool:
    """Zwei Quader (x, y, z, w, d, h) überlappen in einem Rauminhalt über null (Berührung zählt nicht)."""
    return a[0] < b[0] + b[3] and b[0] < a[0] + a[3] and a[1] < b[1] + b[4] and b[1] < a[1] + a[4] and a[2] < b[2] + b[5] and b[2] < a[2] + a[5]


def ueber(b, a) -> bool:
    """Liegt Quader b (x, y, z, w, d, h) über Quader a: Grundflächen mit Fläche über null überlappend, und b beginnt nicht tiefer, als a endet."""
    return b[2] >= a[2] + a[5] and b[0] < a[0] + a[3] and a[0] < b[0] + b[3] and b[1] < a[1] + a[4] and a[1] < b[1] + b[4]


def _pruefe(kisten, stopp, stapelbar, cap: int):
    if not len(stopp) == len(stapelbar) == len(kisten):
        raise ValueError("zu jedem Quader gehören genau ein Stopp und eine Angabe zur Stapelbarkeit")
    for k in kisten:
        if len(k) != 3 or any(not isinstance(x, int) or x <= 0 or x > cap for x in k):
            raise ValueError(f"Quader {k!r} ungültig (drei ganze Maße, je 1 bis {cap})")
    if any((not isinstance(s, int)) or s < 1 for s in stopp):
        raise ValueError("Stopps sind ganze Zahlen ab 1")


def packung_pruefen(kisten, platz, cap: int, vollstaendig: bool = True) -> bool:
    """Unabhängiger Prüfer: jeder Quader höchstens einmal (bei `vollstaendig` genau einmal), ganz im Behälter, keine zwei Quader eines Behälters überlappen."""
    nummern = sorted(p[0] for p in platz)
    if vollstaendig and nummern != list(range(len(kisten))):
        return False
    if len(set(nummern)) != len(nummern) or any(not 0 <= i < len(kisten) for i in nummern):
        return False
    je = {}
    for i, b, x, y, z in platz:
        w, d, h = kisten[i]
        if x < 0 or y < 0 or z < 0 or x + w > cap or y + d > cap or z + h > cap:
            return False
        je.setdefault(b, []).append((x, y, z, w, d, h))
    for lst in je.values():
        for a in range(len(lst)):
            for c in range(a + 1, len(lst)):
                if _ueberlappt(lst[a], lst[c]):
                    return False
    return True


def schranken(kisten, cap: int):
    """(Volumenschranke, Zahl der großen Quader, Schranke): das Volumen aller Quader durch das Behältervolumen aufgerundet; die Zahl der Quader, die in allen drei Maßen über die Hälfte reichen; das Größere.
    Die Schranken gelten ohne Stützbedingung, Entladereihenfolge und Stapelbarkeit; mit Bedingungen ist das Optimum nicht kleiner."""
    volumen = -(-sum(w * d * h for w, d, h in kisten) // cap ** 3)
    gross = sum(1 for w, d, h in kisten if 2 * w > cap and 2 * d > cap and 2 * h > cap)
    return volumen, gross, max(volumen, gross)


def schranke(kisten, cap: int) -> int:
    return schranken(kisten, cap)[2]


# --- Stützfläche ------------------------------------------------------------------------------------------------------------------------------------


def _stuetz_gegen(quader, gesetzt) -> float:
    x, y, z, w, d, _h = quader
    if z == 0:
        return 1.0
    flaeche = 0
    for q in gesetzt:
        if q[2] + q[5] == z:
            flaeche += max(0, min(x + w, q[0] + q[3]) - max(x, q[0])) * max(0, min(y + d, q[1] + q[4]) - max(y, q[1]))
    return flaeche / (w * d)


def stuetzflaeche(kisten, platz, i: int) -> float:
    """Anteil der Grundfläche von Quader i, der auf dem Boden oder auf den Oberseiten anderer Quader desselben Behälters aufliegt (1,0 am Boden)."""
    _, b, x, y, z = next(p for p in platz if p[0] == i)
    andere = [(x2, y2, z2, *kisten[j]) for j, bb, x2, y2, z2 in platz if bb == b and j != i]
    return _stuetz_gegen((x, y, z, *kisten[i]), andere)


def stuetz_minimum(kisten, platz) -> float:
    """Kleinste Stützfläche aller Quader der Packung (1,0 bei leerer Packung)."""
    return min((stuetzflaeche(kisten, platz, p[0]) for p in platz), default=1.0)


# --- Verletzungen -----------------------------------------------------------------------------------------------------------------------------------


def _je_behaelter(kisten, platz) -> dict:
    je = {}
    for i, b, x, y, z in platz:
        je.setdefault(b, []).append((i, (x, y, z, *kisten[i])))
    return je


def blockierte_paare(kisten, platz, stopp) -> list:
    """Paare (unten, oben): Quader `oben` liegt über Quader `unten` desselben Behälters und wird später entladen (Stopp größer). `unten` kann erst nach `oben` entladen werden."""
    paare = []
    for lst in _je_behaelter(kisten, platz).values():
        for i, a in lst:
            for j, b in lst:
                if i != j and ueber(b, a) and stopp[j] > stopp[i]:
                    paare.append((i, j))
    return sorted(paare)


def getragene_paare(kisten, platz, stapelbar) -> list:
    """Paare (unten, oben): Quader `oben` liegt über einem nicht stapelbaren Quader `unten` desselben Behälters."""
    paare = []
    for lst in _je_behaelter(kisten, platz).values():
        for i, a in lst:
            if stapelbar[i]:
                continue
            for j, b in lst:
                if i != j and ueber(b, a):
                    paare.append((i, j))
    return sorted(paare)


def verletzungen(kisten, platz, stopp, stapelbar) -> tuple:
    """(Zahl der blockierten Paare, Zahl der Paare über nicht stapelbaren Quadern, Zahl der betroffenen Quader). Betroffen ist jeder Quader, der in mindestens einem solchen Paar vorkommt."""
    a, b = blockierte_paare(kisten, platz, stopp), getragene_paare(kisten, platz, stapelbar)
    return len(a), len(b), len({i for p in a + b for i in p})


def entladen_ab(platz, stopp, bis: int) -> list:
    """Die Platzierungen, die nach dem Entladen der Stopps 1 bis `bis` noch im Fahrzeug sind (Stopp größer als `bis`)."""
    return [p for p in platz if stopp[p[0]] > bis]


def gueltig(kisten, platz, stopp, stapelbar) -> bool:
    """Erfüllt die Packung die Entladereihenfolge und die Stapelbarkeit (keine blockierten Paare, keine Paare über nicht stapelbaren)?"""
    return not blockierte_paare(kisten, platz, stopp) and not getragene_paare(kisten, platz, stapelbar)


# --- Extreme Points ---------------------------------------------------------------------------------------------------------------------------------


def _projiziere(p, achse: int, gesetzt):
    a, b = [k for k in (0, 1, 2) if k != achse]
    wert = 0
    for q in gesetzt:
        qa = q[achse] + q[3 + achse]
        if qa <= p[achse] and q[a] <= p[a] < q[a] + q[3 + a] and q[b] <= p[b] < q[b] + q[3 + b]:
            wert = max(wert, qa)
    r = list(p)
    r[achse] = wert
    return tuple(r)


def _erlaubt(q, i, liste, stopp, stapelbar) -> bool:
    """Darf Quader i an der Lage q neben die gesetzten Quader `liste` ((Nummer, Lage)...)? Prüft beide Richtungen: i über einem gesetzten und ein gesetzter über i."""
    for j, g in liste:
        if ueber(q, g) and (stopp[i] > stopp[j] or not stapelbar[j]):
            return False
        if ueber(g, q) and (stopp[j] > stopp[i] or not stapelbar[i]):
            return False
    return True


def pack(kisten, stopp, stapelbar, order, cap: int, s_min: float = 0.0):
    """Packt die Quader in der Reihenfolge `order` (jeder höchstens einmal, auch ein Anfang der Reihenfolge ist erlaubt). Ein Eckpunkt ist zulässig, wenn der Quader passt, nichts überlappt, die Stützfläche
    mindestens `s_min` ist und die Entladereihenfolge und die Stapelbarkeit gelten. Ohne Bedingung: alle Stopps 1 und alle Quader stapelbar übergeben. Gibt (bins, platz, zustand) zurück:
    bins[b] = Quadernummern, platz = (Quader, Behälter, x, y, z), zustand[b] = die Eckpunkte des Behälters nach dem letzten Quader, sortiert nach (z, y, x)."""
    order = list(order)
    if len(set(order)) != len(order) or any(not 0 <= i < len(kisten) for i in order):
        raise ValueError("die Reihenfolge darf jeden Quader höchstens einmal enthalten")
    if not 0 <= s_min <= 1:
        raise ValueError("die Mindest-Stützfläche liegt zwischen 0 und 1")
    _pruefe(kisten, stopp, stapelbar, cap)
    behaelter = []          # je Behälter: {"punkte": set, "liste": [(Nummer, (x, y, z, w, d, h))]}
    platz = []
    bins = []
    for i in order:
        w, d, h = kisten[i]
        wahl = None
        for b, c in enumerate(behaelter):
            gesetzt = [g for _j, g in c["liste"]]
            for (x, y, z) in sorted(c["punkte"], key=lambda p: (p[2], p[1], p[0])):
                if x + w > cap or y + d > cap or z + h > cap:
                    continue
                k = (x, y, z, w, d, h)
                if any(_ueberlappt(k, q) for q in gesetzt):
                    continue
                if s_min > 0 and _stuetz_gegen(k, gesetzt) < s_min - EPS:
                    continue
                if not _erlaubt(k, i, c["liste"], stopp, stapelbar):
                    continue
                wahl = (b, (x, y, z))
                break
            if wahl:
                break
        if wahl is None:
            behaelter.append({"punkte": {(0, 0, 0)}, "liste": []})
            bins.append([])
            wahl = (len(behaelter) - 1, (0, 0, 0))
        b, (x, y, z) = wahl
        c = behaelter[b]
        platz.append((i, b, x, y, z))
        bins[b].append(i)
        c["punkte"].discard((x, y, z))
        gesetzt = [g for _j, g in c["liste"]]
        for p, achsen in (((x + w, y, z), (1, 2)), ((x, y + d, z), (0, 2)), ((x, y, z + h), (0, 1))):
            if max(p) < cap:
                c["punkte"].add(p)
            for a in achsen:
                q = _projiziere(p, a, gesetzt)
                if max(q) < cap:
                    c["punkte"].add(q)
        c["liste"].append((i, (x, y, z, w, d, h)))
        gesetzt = [g for _j, g in c["liste"]]
        c["punkte"] = {p for p in c["punkte"] if not any(q[0] <= p[0] < q[0] + q[3] and q[1] <= p[1] < q[1] + q[4] and q[2] <= p[2] < q[2] + q[5] for q in gesetzt)}
    return bins, platz, [tuple(sorted(c["punkte"], key=lambda p: (p[2], p[1], p[0]))) for c in behaelter]


def anzahl(kisten, stopp, stapelbar, schluessel: int, cap: int, s_min: float = 0.0) -> int:
    """Behälterzahl der Packung aller Quader mit dem Schlüssel unter den Bedingungen, die `stopp` und `stapelbar` ausdrücken."""
    return len(pack(kisten, stopp, stapelbar, reihenfolge(kisten, stopp, schluessel), cap, s_min)[0])
