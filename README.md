# Entladereihenfolge und Stapelbarkeit – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-entladereihenfolge-demo.streamlit.app/)**

Stück 11 (gelb) der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Stück 9 hat Quader in Behälter gepackt, Stück 10 hat die Stützfläche zur Nebenbedingung gemacht. Diese Demo fügt zwei weitere hinzu, wie sie jede Auslieferung kennt: Jeder Quader hat einen **Stopp** (1 wird zuerst entladen), und manche Quader sind **nicht stapelbar**. Gemessen wird, was das an Behältern kostet und ob es sich lohnt, die Quader nach dem Stopp zu sortieren. Die Fall-Demos zur Stapelplanung zeigen die Anwendung samt Kostenmodell; diese Demo erklärt den Mechanismus davor.

## Warum dieses Problem

Wer eine Tour fährt, packt die Ware des letzten Stopps zuerst ein und die des ersten zuletzt. Eine Packung, die Behälter spart, kann diese Ordnung verletzen: Liegt ein Quader des ersten Stopps unter einem des letzten, muss beim Entladen umgestaut werden. Die naheliegende Antwort („nach dem Stopp sortieren“) stimmt hier **nicht**: Im Zellenmittel ist die Grundfläche als Schlüssel in 55 von 60 Vergleichen mindestens so gut wie Stopp ab (Instanz für Instanz oft gleich), auch wenn die Bedingung zwingend ist, vermutlich weil der Packer die Bedingung beim Setzen ohnehin erzwingt (nicht getestet). Beide Bedingungen zusammen können mehr kosten als jede allein: An einem Beispiel kostet die Entladereihenfolge allein keinen Behälter, die Stapelbarkeit allein auch nicht, beide zusammen einen (im Mittel addieren sich die Kosten etwa).

## Modell

Quader mit ganzzahliger Breite, Tiefe und Höhe, ohne Drehung, in Behältern der Größe 100 mal 100 mal 100, alle vorab bekannt. **Dekodierer:** Extreme Points mit Projektionen aus Stück 9 (eigene Lesart), mit der Mindest-Stützfläche 80 % aus Stück 10; jeder Quader kommt in den ersten Behälter, in dem ein zulässiger Eckpunkt ihn aufnimmt, an den mit kleinstem (z, y, x). **Stopp und Stapelbarkeit:** Jeder Quader bekommt aus zwei Zufallszahlen einen Stopp von 1 bis m und die Eigenschaft „stapelbar“ oder „nicht stapelbar“ (Anteil q nicht stapelbar); beides hängt nicht von den Maßen ab. **„B liegt über A“:** Die Grundflächen überlappen mit Fläche größer als null, und B beginnt nicht tiefer, als A endet. **Entladereihenfolge:** Liegt B über A, darf der Stopp von B nicht größer sein als der von A (sonst muss B entfernt werden, bevor A an der Reihe ist). **Stapelbarkeit:** Über einem nicht stapelbaren Quader liegt nichts. Der Packer lässt einen Eckpunkt nur zu, wenn die Bedingungen für den neuen Quader und für alle bereits gesetzten gelten. **Ignorieren:** Die Demo kann die Bedingungen auch weglassen, zählt dann aber die **blockierten Paare**, die **Paare über nicht stapelbaren Quadern** und die **betroffenen Quader** der fertigen Packung. **Fünf Schlüssel:** Lieferung (Eingabereihenfolge), Volumen, Grundfläche, Stopp ab (der größte Stopp zuerst, dann nach der Grundfläche) und Stopp auf (der kleinste Stopp zuerst, als Gegenprobe). **Schranken:** das Volumen aller Quader durch das Behältervolumen, aufgerundet, und die Zahl der Quader, die in allen drei Maßen über die Hälfte reichen; das Größere von beiden. **Optimum** über alle Packungen mit CP-SAT (nur Generator und Tests; ohne Stützbedingung, mit den Bedingungen an Stopp und Stapelbarkeit). **Vier Verteilungen:** *mittel* (alle Kanten 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *flach* (Breite und Tiefe 30 bis 80, Höhe 5 bis 30). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`elr_algorithm.py`): `reihenfolge`, `pack` (Extreme Points mit Projektionen, Mindest-Stützfläche, Stopp und Stapelbarkeit; liefert Behälter, Platzierungen und die Eckpunkte je Behälter; ein Anfang der Reihenfolge liefert den Zustand nach so vielen Schritten), `ueber` (die „über“-Relation), `verletzungen`, `entladen_ab`, `stuetzflaeche`, `schranken`, `packung_pruefen` (unabhängiger Prüfer).
- **Handbeispiele:** zwei feste Mengen von je zwölf Quadern mit Stopps und Stapelbarkeit. Die App zeichnet einen gewählten Behälter in 3D (Farbe nach Stopp, Stapelbarkeit oder Reihenfolge des Setzens; verletzte Quader rot umrandet) und zeigt alle 20 Kombinationen aus Schlüssel und Bedingung. Der Regler „Entladen bis Stopp“ nimmt die Quader bis zu diesem Stopp aus der Zeichnung und zählt, welche unter einem später zu entladenden lagen.
- **Messraster:** vier Verteilungen × drei Quaderzahlen (20, 40, 80) × **100 feste Instanzen** je Zelle × fünf Schlüssel × sechs Bedingungen (ohne und fünf Kombinationen aus Stopps und Anteil nicht stapelbar), immer mit der Mindest-Stützfläche 80 %. Maßstab ist die Schranke (vermutlich locker, wie in Stück 9 gemessen; ein Optimum mit Stützbedingung gibt es nicht). Die Summen stehen als ganze Zahlen in `elr_precomputed.json` (erzeugt von `generate_precomputed.py`).
- **Orakel:** bei 12 Quadern 40 Instanzen je Verteilung und Anteil nicht stapelbar (0, 20, 40 %), 3 Stopps, CP-SAT mit 20 Sekunden Zeitlimit je Lauf, **ohne Stützbedingung** (sie lässt sich nicht linear ausdrücken).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_entladereihenfolge.py`. Tabellenwerte sind Mittel über die Instanzen einer Zelle von (Behälter minus Schranke).

| Frage | Befund |
|---|---|
| Beispiel 1 (zwölf breit gestreute Quader, Optimum 1) | Ohne Bedingung brauchen alle fünf Schlüssel **1** Behälter. Mit 3 Stopps und 20 % nicht stapelbar bleibt **nur die Grundfläche bei 1**, die anderen vier brauchen 2 (Tabelle unten). Lieferung kostet schon die Stapelbarkeit allein einen Behälter, Stopp auf schon die Entladereihenfolge allein |
| Beispiel 2 (zwölf mittlere Quader, Optimum 1) | Die Grundfläche braucht ohne Bedingung 1, mit der Entladereihenfolge allein 1, mit der Stapelbarkeit allein 1, mit **beiden 2**. Die Heuristik zahlt hier mehr, als die Aufgabe verlangt |
| Was kosten die Bedingungen? | Im Mittel über die zwölf Zellen mit der Grundfläche **+0,30 / +0,48 / +0,66 / +1,27 / +2,27** Behälter bei 2 Stopps, 3 Stopps, 5 Stopps, 3 Stopps mit 20 % und 3 Stopps mit 40 % nicht stapelbar (Tabelle B). Flache Quader zahlen am meisten (n = 80, 3 Stopps und 40 %: 4,01 → 13,48) |
| Instanz für Instanz | Von 1200 Instanzen braucht die Grundfläche mit den fünf Bedingungen in **373 / 512 / 620 / 798 / 990** mehr Behälter als ohne Bedingung, Stopp ab in **500 / 647 / 760 / 908 / 1051** |
| Hilft es, nach dem Stopp zu sortieren? | **Nein, meistens nicht.** Ohne Bedingung sind Grundfläche, Stopp ab und Stopp auf gleich (alle Stopps sind 1, die Packung ist dieselbe). Mit Bedingung ist die Grundfläche allein der beste Schlüssel in **11 / 8 / 9 / 11 / 12** von 12 Zellen (in der Reihenfolge der Bedingungen aus Tabelle A); Stopp ab schlägt sie nur bei 3 Stopps (in 2 Zellen) und bei 5 Stopps (in 3 Zellen), bei den anderen drei Bedingungen nie. Volumen und Lieferung sind in jeder Zelle schlechter, Stopp auf (Gegenprobe) ebenso. Stopp ab kostet im Mittel +0,44 / +0,64 / +0,84 / +1,55 / +2,62 Behälter |
| Was würde beim Ignorieren klemmen? | Packt man ohne Bedingung (Grundfläche) und misst an 3 Stopps, sind je nach Zelle **28,2 bis 74,1 %** der Quader von einer Blockierung betroffen, im Mittel **3,4 bis 66,3** blockierte Paare je Instanz (2 Stopps: 19,5 bis 63,0 % und 2,3 bis 50,6 Paare; 5 Stopps: 33,5 bis 80,9 % und 4,1 bis 79,4 Paare). Flache Quader leiden am meisten (n = 80, 3 Stopps: 66,3 Paare, 74 %) |
| Was wäre im besten Fall möglich? | Das **Orakel** (n = 12, 3 Stopps, freie Platzierung, alle 480 Instanzen entschieden): Im Optimum brauchen die Bedingungen in **5** von 160 Instanzen mehr Behälter, wenn alle stapelbar sind, in **38** von 160 bei 20 % und in **63** von 160 bei 40 % nicht stapelbar. Kleine Quader kosten nie etwas (0 von 120), flache am meisten (bei 40 %: 36 von 40, im Mittel 1,62 → 3,33 Behälter) |
| Wie weit liegt die Heuristik daneben? | Die Heuristik (Grundfläche) trifft das Optimum mit Bedingungen in **286** von 480 Instanzen. Im Mittel kosten die Bedingungen im Optimum +0,03 (3 Stopps) beziehungsweise +0,59 (mit 40 % nicht stapelbar) Behälter, in der Heuristik +0,23 beziehungsweise +0,74 (Differenzen der ungerundeten Mittel) |

**Beispiel 1** (Behälterzahl je Schlüssel und Bedingung; 3 Stopps, 20 % nicht stapelbar):

| Schlüssel | ohne Bedingung | nur Entladereihenfolge | nur Stapelbarkeit | beide Bedingungen |
|---|---|---|---|---|
| Lieferung | 1 | 1 | 2 | 2 |
| Volumen | 1 | 1 | 1 | 2 |
| Grundfläche | 1 | 1 | 1 | 1 |
| Stopp ab | 1 | 1 | 1 | 2 |
| Stopp auf | 1 | 2 | 1 | 2 |

**Beispiel 2:**

| Schlüssel | ohne Bedingung | nur Entladereihenfolge | nur Stapelbarkeit | beide Bedingungen |
|---|---|---|---|---|
| Lieferung | 2 | 2 | 2 | 2 |
| Volumen | 1 | 2 | 1 | 2 |
| Grundfläche | 1 | 1 | 1 | 2 |
| Stopp ab | 1 | 2 | 1 | 2 |
| Stopp auf | 1 | 2 | 1 | 2 |

**Tabelle A: Behälter über der Schranke für die Grundfläche** (Mittel über 100 Instanzen je Zelle; ohne Bedingung und mit den fünf Kombinationen aus Stopps m und Anteil nicht stapelbar q; kein Optimum, die Schranke ist vermutlich locker, dort zählt nur der Vergleich der Kombinationen):

| Verteilung | n | ohne | m = 2 | m = 3 | m = 5 | m = 3, q = 0,2 | m = 3, q = 0,4 |
|---|---|---|---|---|---|---|---|
| mittel | 20 | 0,92 | 0,99 | 1,04 | 1,03 | 1,23 | 1,44 |
| mittel | 40 | 1,67 | 1,81 | 1,96 | 2,00 | 2,28 | 2,76 |
| mittel | 80 | 2,54 | 2,65 | 2,75 | 2,85 | 3,66 | 4,72 |
| breit | 20 | 1,12 | 1,19 | 1,34 | 1,36 | 1,54 | 1,66 |
| breit | 40 | 1,63 | 1,81 | 1,92 | 2,02 | 2,25 | 2,71 |
| breit | 80 | 2,35 | 2,61 | 2,73 | 2,89 | 3,37 | 4,26 |
| klein | 20 | 0,06 | 0,26 | 0,47 | 0,67 | 0,62 | 0,83 |
| klein | 40 | 0,82 | 1,00 | 1,00 | 1,01 | 1,07 | 1,35 |
| klein | 80 | 0,48 | 0,82 | 0,96 | 1,02 | 1,21 | 1,93 |
| flach | 20 | 1,66 | 2,20 | 2,45 | 2,88 | 3,31 | 4,31 |
| flach | 40 | 2,33 | 3,10 | 3,38 | 3,84 | 5,40 | 7,40 |
| flach | 80 | 4,01 | 4,75 | 5,30 | 5,89 | 8,90 | 13,48 |

**Tabelle B: dasselbe für alle fünf Schlüssel** (Mittel der zwölf Zellenwerte):

| Schlüssel | ohne | m = 2 | m = 3 | m = 5 | m = 3, q = 0,2 | m = 3, q = 0,4 |
|---|---|---|---|---|---|---|
| Lieferung | 2,85 | 3,36 | 3,63 | 3,95 | 4,54 | 5,52 |
| Volumen | 2,20 | 2,69 | 2,90 | 3,15 | 3,74 | 4,69 |
| Grundfläche | 1,63 | 1,93 | 2,11 | 2,29 | 2,90 | 3,90 |
| Stopp ab | 1,63 | 2,07 | 2,27 | 2,47 | 3,18 | 4,25 |
| Stopp auf | 1,63 | 2,31 | 2,85 | 3,72 | 3,71 | 4,67 |

**Tabelle C: Verletzungen in der Packung ohne Bedingung** (Schlüssel Grundfläche, gemessen an 3 Stopps; Mittel über 100 Instanzen; „betroffen“ = Anteil der Quader, die an einem blockierten Paar beteiligt sind):

| Verteilung | n | blockierte Paare je Instanz | betroffene Quader |
|---|---|---|---|
| mittel | 20 | 4,2 | 33 % |
| mittel | 40 | 10,1 | 39 % |
| mittel | 80 | 20,6 | 40 % |
| breit | 20 | 3,9 | 29 % |
| breit | 40 | 12,7 | 40 % |
| breit | 80 | 29,8 | 44 % |
| klein | 20 | 3,4 | 28 % |
| klein | 40 | 19,6 | 57 % |
| klein | 80 | 41,2 | 59 % |
| flach | 20 | 12,5 | 63 % |
| flach | 40 | 29,4 | 68 % |
| flach | 80 | 66,3 | 74 % |

**Tabelle D: Orakel** (CP-SAT, n = 12, 3 Stopps, ohne Stützbedingung, Mittel über je 40 entschiedene Instanzen; „Heuristik“ = Grundfläche; „trifft“ = Zahl der Instanzen, in denen die Heuristik das Optimum mit Bedingungen erreicht):

| Verteilung | nicht stapelbar | Optimum ohne Bedingung | Optimum mit Bedingungen | mehr Behälter im Optimum | Heuristik ohne | Heuristik mit | Heuristik trifft das Optimum |
|---|---|---|---|---|---|---|---|
| mittel | 0 % | 1,57 | 1,60 | 1 von 40 | 2,00 | 2,05 | 22 |
| breit | 0 % | 1,38 | 1,45 | 3 von 40 | 1,73 | 2,02 | 18 |
| klein | 0 % | 1,00 | 1,00 | 0 von 40 | 1,00 | 1,02 | 39 |
| flach | 0 % | 1,62 | 1,65 | 1 von 40 | 1,80 | 2,35 | 15 |
| mittel | 20 % | 1,57 | 1,75 | 7 von 40 | 2,00 | 2,12 | 25 |
| breit | 20 % | 1,38 | 1,60 | 9 von 40 | 1,73 | 2,17 | 17 |
| klein | 20 % | 1,00 | 1,00 | 0 von 40 | 1,00 | 1,02 | 39 |
| flach | 20 % | 1,62 | 2,30 | 22 von 40 | 1,80 | 3,10 | 11 |
| mittel | 40 % | 1,57 | 1,82 | 10 von 40 | 2,00 | 2,33 | 20 |
| breit | 40 % | 1,38 | 1,80 | 17 von 40 | 1,73 | 2,27 | 21 |
| klein | 40 % | 1,00 | 1,00 | 0 von 40 | 1,00 | 1,05 | 38 |
| flach | 40 % | 1,62 | 3,33 | 36 von 40 | 1,80 | 3,85 | 21 |

## Ehrliche Grenzen

- Alle Aussagen gelten für Quader ohne Drehung, vier Verteilungen mit festen Bereichen, Quaderzahlen 20, 40 und 80 im Raster (12 beim Orakel), eine Behältergröße, **zufällige Stopps und Stapelbarkeit** (keine Praxisdaten, unabhängig von den Maßen) und **einen** Dekodierer (Extreme Points mit Projektionen, eigene Lesart) mit der Wahl „tiefster, hinterster, linkester Eckpunkt“. Stapellast, Gewichtsgrenzen, Drehung und die seitliche Zufahrt zur Tür kommen nicht vor; geprüft wird nur die Blockierung von oben.
- Die Raster-Tabellen gelten mit der Mindest-Stützfläche 80 %. Ein **Optimum mit Stützbedingung** fehlt (die Stützfläche ist im CP-SAT-Modell nicht abgebildet); das Orakel gilt ohne sie, **und es darf Quader frei anordnen**. Es zeigt, wann die Bedingungen die Aufgabe selbst teurer machen, nicht, was mit Stützfläche optimal wäre.
- Die Verletzungen hängen am Schlüssel und an der Mindest-Stützfläche, mit denen ohne Bedingung gepackt wird (Grundfläche, 80 %).
- Die Projektionen der Eckpunkte sind nach eigener Lesart umgesetzt (Stück 9); es wird keine Zahl und keine Aussage der Literatur übernommen.
- Was Umstauen kostet, misst die Demo nicht (siehe die Umstauen-Linie); zur **Laufzeit** macht sie keine Aussage.

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

**Annahmen.** Quader mit ganzzahligen Maßen (Breite, Tiefe, Höhe), ohne Drehung; Behälter 100 mal 100 mal 100; alle Quader sind vor dem Packen bekannt; jeder Quader kommt in den ersten Behälter, in dem ein Eckpunkt ihn aufnimmt (Stück 9, Extreme Points mit Projektionen), optional unter der Mindest-Stützfläche 80 % (Stück 10). Jeder Quader hat einen **Stopp** (1 wird zuerst entladen) und ist **stapelbar oder nicht**; beides ist zufällig und hängt nicht von den Maßen ab. **Entladereihenfolge:** Liegt Quader B über Quader A desselben Behälters (die Grundflächen überlappen, und B beginnt nicht tiefer, als A endet), darf der Stopp von B nicht größer sein als der von A. **Stapelbarkeit:** Über einem nicht stapelbaren Quader liegt nichts. Geprüft wird nur diese Blockierung von oben, nicht die seitliche Zufahrt zur Tür.

**Grenzen.** Das Messraster deckt vier Verteilungen der Kanten und drei Quaderzahlen (20, 40, 80) ab, jeweils mit 100 Instanzen je Zelle, fünf Schlüssel und fünf Kombinationen aus Stopps (2, 3, 5) und Anteil nicht stapelbar (0, 20, 40 %), immer mit der Mindest-Stützfläche 80 %. Die Wahl unter den Eckpunkten ist immer der mit kleinstem (z, y, x). Ein Optimum mit Stützbedingung fehlt (sie ist im CP-SAT-Modell nicht abgebildet); das Orakel (CP-SAT, 20 Sekunden Zeitlimit je Lauf) gilt ohne Stützbedingung, nur bei 12 Quadern und 3 Stopps. Die Projektionen der Eckpunkte sind nach eigener Lesart umgesetzt (Stück 9). Stopps und Stapelbarkeit sind zufällig, keine Praxisdaten; Stapellast, Gewicht, Drehung und die Zufahrt zur Tür kommen nicht vor.

**Bekannte Probleme und Unsicherheiten.** Die Verletzungen der Packung ohne Bedingung hängen am Schlüssel und an der Mindest-Stützfläche, mit denen sie gepackt wird; die Zahlen im Raster gelten für die Grundfläche mit 80 %. Wer die Bedingungen ignoriert, muss beim Entladen umstauen; wie teuer das ist, misst die Demo nicht (siehe die Umstauen-Linie). Zur Laufzeit macht die Demo keine Aussage. Die App wurde im Browser bedient (Presets, Würfel-Button, Regler und die 3D-Ansicht auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät.

## Verifikation

- **Kern:** alle Regeln an einer von Hand gerechneten Mini-Instanz (vier Quader mit Stopps, Behälter 10 mal 10 mal 10: die „über“-Relation, die Packung ohne Bedingung und die Packung mit Entladereihenfolge); Stützfläche; beide Handbeispiele mit allen 20 Behälterzahlen; unabhängiger Packungsprüfer; Randfälle (leere Eingabe, ein Quader, Quader gleich Behälter, Berührung ohne Überlappung, Gleichstände, ungültige Eingaben, Grenzen der Regler).
- **Orakel** (`tests/test_oracle_entladereihenfolge.py`): der Dekodierer mit allen Bedingungen gegen eine Umsetzung, die die Eckpunkte nach jedem Quader neu erzeugt und die Stützfläche aus einem Voxelraster liest; die „über“-Relation gegen eine Zellenzählung; CP-SAT an Fällen, deren Optimum von Hand feststeht (zwei Quader 10 mal 10 mal 4: beide nicht stapelbar braucht zwei Behälter, sonst einen).
- **Messraster:** jede Zelle bei n = 20 wird frisch gerechnet und exakt mit `elr_precomputed.json` verglichen, bei allen Zellen die ersten drei Instanzen einzeln (Stichprobe in der Datei); alle Zellen zusammen prüft `python generate_precomputed.py --check` (parallel). Das Orakel wird an einer Stichprobe mit CP-SAT nachgerechnet; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **3D-Darstellung:** Die zwölf Dreiecke je Quader decken jede der sechs Seitenflächen lückenlos und ohne Überlappung ab; die Farbe folgt dem Stopp, der Stapelbarkeit oder der Reihenfolge (`tests/test_visualization.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung, jeder Hilfetext stimmt mit der Rechnung überein; Schnellstart oben in der Seitenleiste, fester Kopf (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Zahlenfelder an den Grenzen) und Footer-Test.
- **Tests gesamt:** 148 Tests, alle grün.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/opt.py` | exaktes Optimum mit CP-SAT, mit und ohne Bedingungen (nur für Generator und Tests) |
| `dev/readme_bauen.py`, `dev/readme_vorlage.md` | setzen die README aus der Vorlage, den Tabellen der Messzellen und dem Text der Annahmen zusammen |
| `elr_algorithm.py` | Kern: Schlüssel, Dekodierer mit Stützfläche, Stopp und Stapelbarkeit, „über“-Relation, Verletzungen, Schranken, Packungsprüfer |
| `elr_constants.py` | Beispiele, Reglerwerte, Messraster, Farben, Presets, Text der Annahmen |
| `elr_evaluation.py` | Analyse, Verdikte, Messzellen |
| `elr_layout.py` | Fester Kopf (Stylesheet) und Tabellen auf dem Telefon |
| `elr_precomputed.json` | vorberechnete Summen, Orakel und Stichprobe des Messrasters |
| `elr_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `elr_scenario.py` | Instanzen: Handbeispiele und Zufallsinstanzen mit Stopps und Stapelbarkeit aus festen Seeds |
| `elr_visualization.py` | Plotly-Abbildungen (3D-Behälter mit Farbe nach Stopp, Stapelbarkeit oder Reihenfolge; Balken mit gesperrten Achsen) |
| `generate_precomputed.py` | erzeugt `elr_precomputed.json` (Messraster, Orakel mit CP-SAT, Stichprobe); `--check` vergleicht, `--keep-orakel` behält das gespeicherte Orakel, `--nur-stichprobe` ergänzt die Stichprobe |
| `requirements-dev.txt` | Laufzeit plus pytest und ortools |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanz und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, 3D-Darstellung, Messraster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Umstauen und seine Kosten:** Wie teuer das Umstauen einer verletzten Packung ist, behandelt die Umstauen-Linie; hier wird nur gezählt, was klemmen würde.
- **Stapellast, Gewichtsgrenzen, Drehung, seitliche Zufahrt zur Tür:** nicht Gegenstand dieses Stücks.
- **Optimum mit Stützbedingung:** nicht linear ausdrückbar; kein Optimum, nur Schranke und Vergleich.
- **Laufzeitvergleich:** hängt an der Umsetzung, keine Aussage.
- **Gütegarantien und Zahlen aus der Literatur:** keine übernommen; die Fall-Demos zur Stapelplanung und zum Beladeplan werden nur verwiesen, keine Zahl von dort übernommen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
