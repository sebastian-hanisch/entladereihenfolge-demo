# Entladereihenfolge und Stapelbarkeit – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-entladereihenfolge-demo.streamlit.app/)**

Stück 11 (gelb) der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Stück 9 hat Quader in Behälter gepackt, Stück 10 hat die Stützfläche zur Nebenbedingung gemacht. Diese Demo fügt zwei weitere hinzu, wie sie jede Auslieferung kennt: Jeder Quader hat einen **Stopp** (1 wird zuerst entladen), und manche Quader sind **nicht stapelbar**. Gemessen wird, was das an Behältern kostet und ob es sich lohnt, die Quader nach dem Stopp zu sortieren. Die Fall-Demos zur Stapelplanung zeigen die Anwendung samt Kostenmodell; diese Demo erklärt den Mechanismus davor.

## Warum dieses Problem

Wer eine Tour fährt, packt die Ware des letzten Stopps zuerst ein und die des ersten zuletzt. Eine Packung, die Behälter spart, kann diese Ordnung verletzen: Liegt ein Quader des ersten Stopps unter einem des letzten, muss beim Entladen umgestaut werden. Die naheliegende Antwort („nach dem Stopp sortieren“) stimmt hier **nicht**: Bei den gemessenen Instanzen ist die Grundfläche als Schlüssel fast immer besser, auch wenn die Bedingung zwingend ist, weil der Packer die Bedingung beim Setzen ohnehin erzwingt. Und die beiden Bedingungen verschärfen sich gegenseitig: An einem Beispiel kostet die Entladereihenfolge allein keinen Behälter, die Stapelbarkeit allein auch nicht, beide zusammen einen.

## Modell

Quader mit ganzzahliger Breite, Tiefe und Höhe, ohne Drehung, in Behältern der Größe 100 mal 100 mal 100, alle vorab bekannt. **Dekodierer:** Extreme Points mit Projektionen aus Stück 9 (eigene Lesart), mit der Mindest-Stützfläche 80 % aus Stück 10; jeder Quader kommt in den ersten Behälter, in dem ein zulässiger Eckpunkt ihn aufnimmt, an den mit kleinstem (z, y, x). **Stopp und Stapelbarkeit:** Jeder Quader bekommt aus zwei Zufallszahlen einen Stopp von 1 bis m und die Eigenschaft „stapelbar“ oder „nicht stapelbar“ (Anteil q nicht stapelbar); beides hängt nicht von den Maßen ab. **„B liegt über A“:** Die Grundflächen überlappen mit Fläche größer als null, und B beginnt nicht tiefer, als A endet. **Entladereihenfolge:** Liegt B über A, darf der Stopp von B nicht größer sein als der von A (sonst muss B entfernt werden, bevor A an der Reihe ist). **Stapelbarkeit:** Über einem nicht stapelbaren Quader liegt nichts. Der Packer lässt einen Eckpunkt nur zu, wenn die Bedingungen für den neuen Quader und für alle bereits gesetzten gelten. **Ignorieren:** Die Demo kann die Bedingungen auch weglassen, zählt dann aber die **blockierten Paare**, die **Paare über nicht stapelbaren Quadern** und die **betroffenen Quader** der fertigen Packung. **Fünf Schlüssel:** Lieferung (Eingabereihenfolge), Volumen, Grundfläche, Stopp ab (der größte Stopp zuerst, dann nach der Grundfläche) und Stopp auf (der kleinste Stopp zuerst, als Gegenprobe). **Schranken:** das Volumen aller Quader durch das Behältervolumen, aufgerundet, und die Zahl der Quader, die in allen drei Maßen über die Hälfte reichen; das Größere von beiden. **Optimum** über alle Packungen mit CP-SAT (nur Generator und Tests; ohne Stützbedingung, mit den Bedingungen an Stopp und Stapelbarkeit). **Vier Verteilungen:** *mittel* (alle Kanten 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *flach* (Breite und Tiefe 30 bis 80, Höhe 5 bis 30). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`elr_algorithm.py`): `reihenfolge`, `pack` (Extreme Points mit Projektionen, Mindest-Stützfläche, Stopp und Stapelbarkeit; liefert Behälter, Platzierungen und die Eckpunkte je Behälter; ein Anfang der Reihenfolge liefert den Zustand nach so vielen Schritten), `ueber` (die „über“-Relation), `verletzungen`, `entladen_ab`, `stuetzflaeche`, `schranken`, `packung_pruefen` (unabhängiger Prüfer).
- **Handbeispiele:** zwei feste Mengen von je zwölf Quadern mit Stopps und Stapelbarkeit. Die App zeichnet einen gewählten Behälter in 3D (Farbe nach Stopp, Stapelbarkeit oder Reihenfolge des Setzens; verletzte Quader rot umrandet) und zeigt alle 20 Kombinationen aus Schlüssel und Bedingung. Der Regler „Entladen bis Stopp“ nimmt die Quader bis zu diesem Stopp aus der Zeichnung und zählt, welche unter einem später zu entladenden lagen.
- **Messraster:** vier Verteilungen × drei Quaderzahlen (20, 40, 80) × **100 feste Instanzen** je Zelle × fünf Schlüssel × sechs Bedingungen (ohne und fünf Kombinationen aus Stopps und Anteil nicht stapelbar), immer mit der Mindest-Stützfläche 80 %. Maßstab ist die Schranke (locker; ein Optimum mit Stützbedingung gibt es nicht). Die Summen stehen als ganze Zahlen in `elr_precomputed.json` (erzeugt von `generate_precomputed.py`).
- **Orakel:** bei 12 Quadern 40 Instanzen je Verteilung und Anteil nicht stapelbar (0, 20, 40 %), 3 Stopps, CP-SAT mit 20 Sekunden Zeitlimit je Lauf, **ohne Stützbedingung** (sie lässt sich nicht linear ausdrücken).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_entladereihenfolge.py`. Tabellenwerte sind Mittel über die Instanzen einer Zelle von (Behälter minus Schranke).

| Frage | Befund |
|---|---|
| Beispiel 1 (zwölf breit gestreute Quader, Optimum 1) | Ohne Bedingung brauchen alle fünf Schlüssel **1** Behälter. Mit 3 Stopps und 20 % nicht stapelbar bleibt **nur die Grundfläche bei 1**, die anderen vier brauchen 2 (Tabelle unten). Lieferung kostet schon die Stapelbarkeit allein einen Behälter, Stopp auf schon die Entladereihenfolge allein |
| Beispiel 2 (zwölf mittlere Quader, Optimum 1) | Die Grundfläche braucht ohne Bedingung 1, mit der Entladereihenfolge allein 1, mit der Stapelbarkeit allein 1, mit **beiden 2**. Die Heuristik zahlt hier mehr, als die Aufgabe verlangt |
| Was kosten die Bedingungen? | Im Mittel über die zwölf Zellen mit der Grundfläche **+{{K_G1}} / +{{K_G2}} / +{{K_G3}} / +{{K_G4}} / +{{K_G5}}** Behälter bei 2 Stopps, 3 Stopps, 5 Stopps, 3 Stopps mit 20 % und 3 Stopps mit 40 % nicht stapelbar (Tabelle B). Flache Quader zahlen am meisten (n = 80, 3 Stopps und 40 %: 4,01 → 13,48) |
| Instanz für Instanz | Von 1200 Instanzen braucht die Grundfläche mit den fünf Bedingungen in **{{M_G}}** mehr Behälter als ohne Bedingung, Stopp ab in **{{M_S}}** |
| Hilft es, nach dem Stopp zu sortieren? | **Nein, meistens nicht.** Ohne Bedingung sind Grundfläche, Stopp ab und Stopp auf gleich (alle Stopps sind 1, die Packung ist dieselbe). Mit Bedingung ist die Grundfläche allein der beste Schlüssel in **{{B_G}}** von 12 Zellen (in der Reihenfolge der Bedingungen aus Tabelle A); Stopp ab schlägt sie nur bei 3 Stopps (in 2 Zellen) und bei 5 Stopps (in 3 Zellen), bei den anderen drei Bedingungen nie. Volumen und Lieferung sind in jeder Zelle schlechter, Stopp auf (Gegenprobe) ebenso. Stopp ab kostet im Mittel +{{S_1}} / +{{S_2}} / +{{S_3}} / +{{S_4}} / +{{S_5}} Behälter |
| Was würde beim Ignorieren klemmen? | Packt man ohne Bedingung (Grundfläche) und misst an 3 Stopps, sind je nach Zelle **28,2 bis 74,1 %** der Quader von einer Blockierung betroffen, im Mittel **3,4 bis 66,3** blockierte Paare je Instanz (2 Stopps: 19,5 bis 63,0 % und 2,3 bis 50,6 Paare; 5 Stopps: 33,5 bis 80,9 % und 4,1 bis 79,4 Paare). Flache Quader leiden am meisten (n = 80, 3 Stopps: 66,3 Paare, 74 %) |
| Was wäre im besten Fall möglich? | Das **Orakel** (n = 12, 3 Stopps, freie Platzierung, alle 480 Instanzen entschieden): Im Optimum brauchen die Bedingungen in **5** von 160 Instanzen mehr Behälter, wenn alle stapelbar sind, in **38** von 160 bei 20 % und in **63** von 160 bei 40 % nicht stapelbar. Kleine Quader kosten nie etwas (0 von 120), flache am meisten (bei 40 %: 36 von 40, im Mittel 1,62 → 3,33 Behälter) |
| Wie weit liegt die Heuristik daneben? | Die Heuristik (Grundfläche) trifft das Optimum mit Bedingungen in **286** von 480 Instanzen. Im Mittel kosten die Bedingungen im Optimum +0,04 (3 Stopps) beziehungsweise +0,60 (mit 40 % nicht stapelbar) Behälter, in der Heuristik +0,23 beziehungsweise +0,75 |

**Beispiel 1** (Behälterzahl je Schlüssel und Bedingung; 3 Stopps, 20 % nicht stapelbar):

{{BEISPIEL_1}}

**Beispiel 2:**

{{BEISPIEL_2}}

**Tabelle A: Behälter über der Schranke für die Grundfläche** (Mittel über 100 Instanzen je Zelle; ohne Bedingung und mit den fünf Kombinationen aus Stopps m und Anteil nicht stapelbar q; kein Optimum, die Schranke ist locker, dort zählt nur der Vergleich der Kombinationen):

{{TABELLE_A}}

**Tabelle B: dasselbe für alle fünf Schlüssel** (Mittel der zwölf Zellenwerte):

{{TABELLE_B}}

**Tabelle C: Verletzungen in der Packung ohne Bedingung** (Schlüssel Grundfläche, gemessen an 3 Stopps; Mittel über 100 Instanzen; „betroffen“ = Anteil der Quader, die an einem blockierten Paar beteiligt sind):

{{TABELLE_C}}

**Tabelle D: Orakel** (CP-SAT, n = 12, 3 Stopps, ohne Stützbedingung, Mittel über je 40 entschiedene Instanzen; „Heuristik“ = Grundfläche; „trifft“ = Zahl der Instanzen, in denen die Heuristik das Optimum mit Bedingungen erreicht):

{{TABELLE_D}}

## Ehrliche Grenzen

- Alle Aussagen gelten für Quader ohne Drehung, vier Verteilungen mit festen Bereichen, Quaderzahlen 20, 40 und 80 im Raster (12 beim Orakel), eine Behältergröße, **zufällige Stopps und Stapelbarkeit** (keine Praxisdaten, unabhängig von den Maßen) und **einen** Dekodierer (Extreme Points mit Projektionen, eigene Lesart) mit der Wahl „tiefster, hinterster, linkester Eckpunkt“. Stapellast, Gewichtsgrenzen, Drehung und die seitliche Zufahrt zur Tür kommen nicht vor; geprüft wird nur die Blockierung von oben.
- Die Raster-Tabellen gelten mit der Mindest-Stützfläche 80 %. Ein **Optimum mit Stützbedingung** fehlt (CP-SAT kann die Stützfläche nicht linear ausdrücken); das Orakel gilt ohne sie, **und es darf Quader frei anordnen**. Es zeigt, wann die Bedingungen die Aufgabe selbst teurer machen, nicht, was mit Stützfläche optimal wäre.
- Die Verletzungen hängen am Schlüssel und an der Mindest-Stützfläche, mit denen ohne Bedingung gepackt wird (Grundfläche, 80 %).
- Die Projektionen der Eckpunkte sind nach eigener Lesart umgesetzt (Stück 9); es wird keine Zahl und keine Aussage der Literatur übernommen.
- Was Umstauen kostet, misst die Demo nicht (siehe die Umstauen-Linie); zur **Laufzeit** macht sie keine Aussage.

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

{{ANNAHMEN}}

## Verifikation

- **Kern:** alle Regeln an einer von Hand gerechneten Mini-Instanz (vier Quader mit Stopps, Behälter 10 mal 10 mal 10: die „über“-Relation, die Packung ohne Bedingung und die Packung mit Entladereihenfolge); Stützfläche; beide Handbeispiele mit allen 20 Behälterzahlen; unabhängiger Packungsprüfer; Randfälle (leere Eingabe, ein Quader, Quader gleich Behälter, Berührung ohne Überlappung, Gleichstände, ungültige Eingaben, Grenzen der Regler).
- **Orakel** (`tests/test_oracle_entladereihenfolge.py`): der Dekodierer mit allen Bedingungen gegen eine Umsetzung, die die Eckpunkte nach jedem Quader neu erzeugt und die Stützfläche aus einem Voxelraster liest; die „über“-Relation gegen eine Zellenzählung; CP-SAT an Fällen, deren Optimum von Hand feststeht (zwei Quader 10 mal 10 mal 4: beide nicht stapelbar braucht zwei Behälter, sonst einen).
- **Messraster:** jede Zelle bei n = 20 wird frisch gerechnet und exakt mit `elr_precomputed.json` verglichen, bei allen Zellen die ersten drei Instanzen einzeln (Stichprobe in der Datei); alle Zellen zusammen prüft `python generate_precomputed.py --check` (parallel). Das Orakel wird an einer Stichprobe mit CP-SAT nachgerechnet; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **3D-Darstellung:** Die zwölf Dreiecke je Quader decken jede der sechs Seitenflächen lückenlos und ohne Überlappung ab; die Farbe folgt dem Stopp, der Stapelbarkeit oder der Reihenfolge (`tests/test_visualization.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung, jeder Hilfetext stimmt mit der Rechnung überein; Schnellstart oben in der Seitenleiste, fester Kopf (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Zahlenfelder an den Grenzen) und Footer-Test.
- **Tests gesamt:** {{TESTS}}.

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
