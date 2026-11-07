"""Instanzen: die Handbeispiele und Zufallsinstanzen (Quader mit Stopps und Stapelbarkeit) für App und Messraster."""

import random
from dataclasses import dataclass

import elr_constants as C


@dataclass(frozen=True)
class Instance:
    kisten: tuple         # Quader als (Breite, Tiefe, Höhe) in Lieferreihenfolge, ganzzahlig und positiv
    u: tuple = ()         # Zufallszahl je Quader in [0, 1): der Stopp bei m Stopps ist 1 + Abrunden von u mal m; leer = 0 für alle (alle Stopps 1)
    w: tuple = ()         # Zufallszahl je Quader in [0, 1): nicht stapelbar, wenn w kleiner als der Anteil q ist; leer = fast 1 für alle (alle stapelbar)
    cap: int = C.CAP      # Kantenlänge eines Behälters

    def __post_init__(self):
        if self.cap <= 0:
            raise ValueError("Kapazität muss positiv sein")
        for t in self.kisten:
            if len(t) != 3 or any((not isinstance(x, int)) or x <= 0 or x > self.cap for x in t):
                raise ValueError(f"Quader {t!r} ungültig (drei ganze Maße, je 1 bis {self.cap})")
        if not self.u:
            object.__setattr__(self, "u", (0.0,) * len(self.kisten))
        if not self.w:
            object.__setattr__(self, "w", (0.999999,) * len(self.kisten))
        if len(self.u) != len(self.kisten) or len(self.w) != len(self.kisten) or any(not 0 <= x < 1 for x in self.u + self.w):
            raise ValueError("zu jedem Quader gehören zwei Zufallszahlen in [0, 1)")

    @property
    def n(self) -> int:
        return len(self.kisten)

    def stopps(self, m: int) -> tuple:
        """Stopp jedes Quaders bei m Stopps (1 bis m); bei m = 1 haben alle Quader den Stopp 1."""
        if m < 1:
            raise ValueError("mindestens ein Stopp")
        return tuple(1 + int(x * m) for x in self.u)

    def stapelbar(self, q: float) -> tuple:
        """Stapelbarkeit jedes Quaders, wenn der Anteil q der Quader nicht stapelbar ist (nicht stapelbar, wenn w kleiner als q ist); bei q = 0 sind alle stapelbar."""
        return tuple(x >= q for x in self.w)


def beispiel(index: int) -> Instance:
    return Instance(tuple(C.BEISPIELE[index]), tuple(C.BEISPIEL_U[index]), tuple(C.BEISPIEL_W[index]), C.CAP)


def mess_seed(verteilung: int, n_index: int, j: int) -> int:
    """Fester Seed der j-ten Instanz einer Zelle des Messrasters (Verteilung 0 bis 3, Index der Quaderzahl); stabil über Läufe und Rechner."""
    return 1_000_000 * (verteilung + 1) + 1_000 * (n_index + 1) + j


def zufallsinstanz(verteilung: int, n: int, seed: int, cap: int = C.CAP) -> Instance:
    """n Quader, Breite, Tiefe und Höhe gleichverteilt (ganzzahlig) in den Bereichen der Verteilung; dazu je Quader zwei Zufallszahlen für Stopp und Stapelbarkeit (eigene Quelle, Seed + 23)."""
    _, _, bereiche = C.VERTEILUNGEN[verteilung]
    rng = random.Random(seed)
    kisten = tuple(tuple(rng.randint(*bereiche[a]) for a in range(3)) for _ in range(n))
    zr = random.Random(seed + 23)
    u = tuple(zr.random() for _ in range(n))
    w = tuple(zr.random() for _ in range(n))
    return Instance(kisten, u, w, cap)


def quelle_instanz(quelle: int, n: int, seed: int) -> Instance:
    """Instanz der App: Quelle 0 und 1 = Handbeispiele (n und seed ohne Wirkung), 2 bis 5 = Zufallsinstanz der Verteilung quelle - 2."""
    if quelle in C.BEISPIELE:
        return beispiel(quelle)
    return zufallsinstanz(quelle - 2, n, seed)
