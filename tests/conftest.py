"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from elr_scenario import Instance  # noqa: E402


@pytest.fixture
def mini():
    """Vier Quader (Breite, Tiefe, Höhe) = (6, 4, 2), (4, 8, 3), (8, 4, 7), (3, 2, 5) mit den Nummern 0 bis 3, Behälter 10 mal 10 mal 10, Volumen 48 + 96 + 224 + 30 = 398, Schranke 1.

    Bei zwei Stopps haben sie die Stopps 1, 2, 2, 2 (die Zufallszahlen u geben 1 + Abrunden von 2 u: 0,1 -> 1, 0,9 -> 2); alle sind stapelbar (w = 0,5 bei q = 0,4 nicht stapelbar kommt nicht vor, q = 0).
    Von Hand gerechnet (Details in tests/test_algorithm.py): Ohne Bedingung liegt Quader 2 bei (0, 0, 3) über Quader 0, obwohl er später entladen wird; mit der Bedingung braucht er einen neuen Behälter."""
    return Instance(((6, 4, 2), (4, 8, 3), (8, 4, 7), (3, 2, 5)), (0.1, 0.9, 0.9, 0.9), (0.5, 0.5, 0.5, 0.5), 10)
