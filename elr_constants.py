"""Konstanten: Regler-Grenzen, feste Beispiele, Messraster, Farben und Presets."""

CAP = 100                 # Behälter 100 x 100 x 100 (Breite, Tiefe, Höhe)

# Beispiel 1 (breit gestreute Quader, n = 12, Seed 7001114): Optimum 1 bei jeder Kombination aus Stopps und Anteil nicht stapelbar (CP-SAT, ohne Stützbedingung). Mit Stützfläche 80 % ohne Bedingung
# braucht jeder Schlüssel 1 Behälter; mit 3 Stopps und 20 % nicht stapelbar nur die Grundfläche 1, alle anderen 2 (Lieferung / Volumen / Grundfläche / Stopp ab / Stopp auf: 2 / 2 / 1 / 2 / 2).
# Beispiel 2 (mittlere Quader, n = 12, Seed 7000004): Optimum 1 bei jeder Kombination; mit Stützfläche 80 % ohne Bedingung 1 (Grundfläche), mit 3 Stopps und 20 % nicht stapelbar brauchen alle
# Schlüssel 2 (Phase 0, in den Tests nachgerechnet): Die Heuristik braucht einen Behälter mehr als das Optimum.
BEISPIELE = {
    0: ((38, 11, 25), (49, 66, 47), (35, 33, 30), (29, 20, 47), (25, 47, 37), (26, 38, 23), (51, 34, 27), (26, 22, 28), (28, 27, 46), (40, 7, 17), (16, 28, 62), (14, 37, 7)),
    1: ((45, 56, 52), (23, 29, 33), (36, 43, 55), (27, 22, 29), (25, 40, 59), (41, 24, 21), (20, 26, 34), (20, 45, 39), (33, 57, 57), (29, 33, 45), (30, 24, 26), (22, 37, 49)),
}
BEISPIEL_U = {
    0: (0.4318276015074871, 0.8507238758003177, 0.7331072337447139, 0.935783653683133, 0.8757691782894927, 0.019984268778072023, 0.8092815805625925, 0.1853096448883762, 0.5456177732751946,
        0.006730068397314826, 0.7148853002964933, 0.2973458232675851),
    1: (0.09887133169509277, 0.9521986273628062, 0.35171242794652824, 0.12091265205707524, 0.49652971706200244, 0.5783870028069408, 0.7731625366231492, 0.7662023199174958, 0.7108249243569538,
        0.048269769585422506, 0.2594067715498841, 0.5218009611753578),
}
BEISPIEL_W = {
    0: (0.4629903364229778, 0.09872357282152011, 0.4006416798781036, 0.13061785004773652, 0.9063088271179631, 0.7723722267956911, 0.2303406517775035, 0.2930475285101306, 0.3996363508539863,
        0.7153964633484151, 0.85795262134414, 0.24550801771083985),
    1: (0.7816195819371219, 0.08363964540303348, 0.6294354926108015, 0.9793865073201751, 0.7414599327351958, 0.5128114639384427, 0.980213531240479, 0.19713962368381766, 0.9728143546909431,
        0.35671255939867763, 0.45409112604852164, 0.2606762006624056),
}
BEISPIEL_OPTIMUM = {0: 1, 1: 1}           # Optimum (CP-SAT, ohne Stützbedingung), gleich für alle zwölf Kombinationen aus Stopps und Anteil nicht stapelbar

QUELLEN = {0: "Beispiel 1 (zwölf Quader)", 1: "Beispiel 2 (zwölf andere Quader)", 2: "zufällig, mittlere Quader", 3: "zufällig, breit gestreute Quader",
           4: "zufällig, kleine Quader", 5: "zufällig, flache Quader"}
ZUFALL_QUELLEN = (2, 3, 4, 5)
N_WERTE = (12, 20, 40)

VERTEILUNGEN = (
    ("mittel", "mittlere Quader (alle Kanten 20 bis 60)", ((20, 60), (20, 60), (20, 60))),
    ("breit", "breit gestreute Quader (alle Kanten 5 bis 70)", ((5, 70), (5, 70), (5, 70))),
    ("klein", "kleine Quader (alle Kanten 10 bis 40)", ((10, 40), (10, 40), (10, 40))),
    ("flach", "flache Quader (Breite und Tiefe 30 bis 80, Höhe 5 bis 30)", ((30, 80), (30, 80), (5, 30))),
)
VERTEILUNG_KURZ = ("mittel", "breit", "klein", "flach")
VERTEILUNG_LANG = ("mittlere Quader", "breit gestreute Quader", "kleine Quader", "flache Quader")
VERTEILUNG_DAT = ("mittleren Quadern", "breit gestreuten Quadern", "kleinen Quadern", "flachen Quadern")

SCHLUESSEL = {0: "Lieferreihenfolge (nicht sortiert)", 1: "nach Volumen (größtes zuerst)", 2: "nach Grundfläche (größte zuerst)",
              3: "nach Stopp fallend, dann Grundfläche (letzter Stopp zuerst)", 4: "nach Stopp aufsteigend, dann Grundfläche (Gegenprobe)"}
SCHLUESSEL_KURZ = {0: "Lieferung", 1: "Volumen", 2: "Grundfläche", 3: "Stopp ab", 4: "Stopp auf"}
SCHLUESSEL_MIT = {0: "der Lieferreihenfolge", 1: "dem Volumen", 2: "der Grundfläche", 3: "dem Stopp fallend und der Grundfläche", 4: "dem Stopp aufsteigend und der Grundfläche"}
LIEFERUNG, VOLUMEN, GRUNDFLAECHE, STOPP_AB, STOPP_AUF = 0, 1, 2, 3, 4

M_WERTE = (1, 2, 3, 5)                    # Zahl der Stopps
M_TEXT = {0: "1 Stopp (keine Entladereihenfolge)", 1: "2 Stopps", 2: "3 Stopps", 3: "5 Stopps"}
Q_WERTE = (0.0, 0.2, 0.4)                 # Anteil der nicht stapelbaren Quader
Q_TEXT = {0: "alle stapelbar", 1: "20 % nicht stapelbar", 2: "40 % nicht stapelbar"}
S_WERTE = (0.0, 0.8)                      # Mindest-Stützfläche
S_TEXT = {0: "keine Stützbedingung", 1: "mindestens 80 % Stützfläche"}
S_KURZ = {0: "0 %", 1: "80 %"}
BEDINGUNGEN = {0: "ohne Bedingung", 1: "nur Entladereihenfolge", 2: "nur Stapelbarkeit", 3: "beide Bedingungen"}
BEDINGUNG_KURZ = {0: "ohne", 1: "nur Entlade", 2: "nur Stapel", 3: "beide"}          # Spaltenköpfe der Tabelle in der App (auf dem Telefon sonst breiter als der Bildschirm)
FARBEN = {0: "Reihenfolge des Setzens", 1: "Stopp", 2: "Stapelbarkeit"}
ENTLADEN_MAX = 5

SEED_MAX, DEFAULT_SEED = 999999, 7

# --- Messraster ---------------------------------------------------------------------------------------------------------------------------
INSTANZEN = 100
MESS_N = (20, 40, 80)
MESS_SMIN = 0.8                           # im Raster gilt die Mindest-Stützfläche 80 %
# Kombinationen (Zahl der Stopps, Anteil nicht stapelbar) des Rasters; die Spalte 0 ist „ohne Bedingung“
KOMBIS = ((2, 0.0), (3, 0.0), (5, 0.0), (3, 0.2), (3, 0.4))
KOMBI_KURZ = ("m = 2", "m = 3", "m = 5", "m = 3, q = 0,2", "m = 3, q = 0,4")
VERLETZUNGS_SCHLUESSEL = GRUNDFLAECHE     # die Verletzungen werden in der Packung ohne Bedingung mit diesem Schlüssel gezählt
ORAKEL_N = 12                             # Quaderzahl des CP-SAT-Orakels
ORAKEL_INSTANZEN = 40                     # Instanzen je Verteilung
ORAKEL_ZEIT = 20.0                        # Sekunden je Lauf
ORAKEL_M = 3
ORAKEL_Q = (0.0, 0.2, 0.4)
STICHPROBE_J = (0, 1, 2)

COLOR_LINE = "#c0392b"
COLOR_PUNKT = "#2F6B65"
KISTEN_FARBEN = ("#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756", "#72b7b2", "#9d755d", "#bab0ac", "#eeca3b", "#ff9da6")
STOPP_FARBEN = ("#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756")           # Stopp 1 bis 5
STAPEL_FARBEN = {True: "#54a24b", False: "#e45756"}
VERFAHREN_FARBEN = {0: "#9d755d", 1: "#4c78a8", 2: "#2F6B65", 3: "#b279a2", 4: "#e45756"}

PRESETS = {
    "Beispiel 1, Grundfläche, 3 Stopps, 20 % nicht stapelbar": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": GRUNDFLAECHE, "m_index": 2, "q_index": 1, "s_index": 1, "anwenden": 1,
                                                                 "schritt": 0, "behaelter": 1, "farbe": 1, "entladen": 0},
    "Beispiel 1, Volumen, 3 Stopps, 20 % nicht stapelbar": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": VOLUMEN, "m_index": 2, "q_index": 1, "s_index": 1, "anwenden": 1,
                                                             "schritt": 0, "behaelter": 1, "farbe": 1, "entladen": 0},
    "Beispiel 2, Volumen, Bedingungen ignoriert, Entladen bis Stopp 1": {"quelle": 1, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": VOLUMEN, "m_index": 2, "q_index": 1, "s_index": 1, "anwenden": 0,
                                                                         "schritt": 0, "behaelter": 1, "farbe": 1, "entladen": 1},
    "Beispiel 2, Grundfläche, 3 Stopps, 20 % nicht stapelbar": {"quelle": 1, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": GRUNDFLAECHE, "m_index": 2, "q_index": 1, "s_index": 1, "anwenden": 1,
                                                                 "schritt": 0, "behaelter": 1, "farbe": 1, "entladen": 0},
    "Flache Quader, 40 Stück, 3 Stopps, 20 % nicht stapelbar": {"quelle": 5, "n_index": 2, "seed": DEFAULT_SEED, "schluessel": GRUNDFLAECHE, "m_index": 2, "q_index": 1, "s_index": 1, "anwenden": 1,
                                                                 "schritt": 0, "behaelter": 1, "farbe": 1, "entladen": 0},
}
PRESET_HELP = {
    "Beispiel 1, Grundfläche, 3 Stopps, 20 % nicht stapelbar": "Zwölf Quader mit je einem Stopp (1 bis 3), 20 % nicht stapelbar: Mit der Grundfläche als Schlüssel bleibt es bei einem Behälter, dem Optimum. Die Farbe zeigt den Stopp: Was oben liegt, wird früher entladen.",
    "Beispiel 1, Volumen, 3 Stopps, 20 % nicht stapelbar": "Dieselben Quader mit dem Volumen als Schlüssel: Mit beiden Bedingungen sind es zwei Behälter statt einem. Die Grundfläche bleibt bei einem.",
    "Beispiel 2, Volumen, Bedingungen ignoriert, Entladen bis Stopp 1": "Zwölf andere Quader, der Packer ignoriert die Bedingungen: Sie passen in einen Behälter, aber vier Paare blockieren, und von den vier Quadern des ersten Stopps lagen zwei unter einem später zu entladenden.",
    "Beispiel 2, Grundfläche, 3 Stopps, 20 % nicht stapelbar": "Weder die Entladereihenfolge allein noch die Stapelbarkeit allein kostet bei diesen Quadern einen Behälter, beide zusammen kosten einen, obwohl das Optimum bei einem liegt.",
    "Flache Quader, 40 Stück, 3 Stopps, 20 % nicht stapelbar": "Vierzig flache Quader: Mit beiden Bedingungen sind es sieben Behälter statt fünf (Schranke 2). Flache Quader zahlen für die Bedingungen am meisten.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Quader mit ganzzahligen Maßen (Breite, Tiefe, Höhe), ohne Drehung; Behälter {CAP} mal {CAP} mal {CAP}; alle Quader sind vor dem Packen bekannt; jeder Quader kommt in den ersten Behälter, in dem ein Eckpunkt ihn aufnimmt (Stück 9, Extreme Points mit Projektionen), optional unter der Mindest-Stützfläche 80 % (Stück 10). Jeder Quader hat einen **Stopp** (1 wird zuerst entladen) und ist **stapelbar oder nicht**; beides ist zufällig und hängt nicht von den Maßen ab. **Entladereihenfolge:** Liegt Quader B über Quader A desselben Behälters (die Grundflächen überlappen, und B beginnt nicht tiefer, als A endet), darf der Stopp von B nicht größer sein als der von A. **Stapelbarkeit:** Über einem nicht stapelbaren Quader liegt nichts. Geprüft wird nur diese Blockierung von oben, nicht die seitliche Zufahrt zur Tür.

**Grenzen.** Das Messraster deckt vier Verteilungen der Kanten und drei Quaderzahlen (20, 40, 80) ab, jeweils mit {INSTANZEN} Instanzen je Zelle, fünf Schlüssel und fünf Kombinationen aus Stopps (2, 3, 5) und Anteil nicht stapelbar (0, 20, 40 %), immer mit der Mindest-Stützfläche 80 %. Die Wahl unter den Eckpunkten ist immer der mit kleinstem (z, y, x). Ein Optimum mit Stützbedingung fehlt (CP-SAT kann sie nicht linear ausdrücken); das Orakel (CP-SAT, {int(ORAKEL_ZEIT)} Sekunden Zeitlimit je Lauf) gilt ohne Stützbedingung, nur bei 12 Quadern und 3 Stopps. Die Projektionen der Eckpunkte sind nach eigener Lesart umgesetzt (Stück 9). Stopps und Stapelbarkeit sind zufällig, keine Praxisdaten; Stapellast, Gewicht, Drehung und die Zufahrt zur Tür kommen nicht vor.

**Bekannte Probleme und Unsicherheiten.** Die Verletzungen der Packung ohne Bedingung hängen am Schlüssel und an der Mindest-Stützfläche, mit denen sie gepackt wird; die Zahlen im Raster gelten für die Grundfläche mit 80 %. Wer die Bedingungen ignoriert, muss beim Entladen umstauen; wie teuer das ist, misst die Demo nicht (siehe die Umstauen-Linie). Zur Laufzeit macht die Demo keine Aussage. Die App wurde im Browser bedient (Presets, Würfel-Button, Regler und die 3D-Ansicht auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
