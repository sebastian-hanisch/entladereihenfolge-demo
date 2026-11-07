"""Packen: Entladereihenfolge und Stapelbarkeit - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 11 der Reihe „Packen: Reihenfolge und Platzierungsregel“ (gelb). Quader mit Stopp und Stapelbarkeit: Was über einem anderen liegt, darf nicht später entladen werden, und nicht stapelbare Quader tragen
nichts. Das Messraster (vorberechnet in elr_precomputed.json) zeigt an je 100 Zufallsinstanzen, was das kostet und ob sich Sortieren nach dem Stopp lohnt.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import elr_algorithm as A
import elr_constants as C
from elr_evaluation import (
    BEDINGUNG_LISTE,
    SCHLUESSEL_LISTE,
    Settings,
    analyse,
    orakel_zeilen,
    verdict_aktuell,
    verdict_entladen,
    verdict_kosten,
    verdict_messung,
    verdict_orakel,
    verdict_tabelle,
    verdict_verletzung,
    verdict_verletzung_raster,
    zeile,
)
from elr_layout import dunkles_design, kopf_css
from elr_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from elr_visualization import build_behaelter, build_messung

st.set_page_config(page_title="Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in elr_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🚚 Entladereihenfolge und Stapelbarkeit")
st.markdown(
    """
Stück 9 und 10 haben Quader in Behälter gepackt, ohne zu fragen, wann sie wieder herauskommen. Hier hat jeder Quader einen **Stopp** (1 wird zuerst entladen) und ist **stapelbar oder nicht**. Zwei Bedingungen: **Was über einem anderen liegt, wird nicht später entladen** (sonst müsste man es erst wegräumen), und **über einem nicht stapelbaren liegt nichts**. Drei Fragen: **Was kosten die Bedingungen in Behältern**, **lohnt es sich, nach dem Stopp zu sortieren**, und **was bleibt vom Optimum übrig**? Die Demo zeigt an zwölf Quadern, wo es klemmt, und an einem Messraster aus je 100 Zufallsinstanzen, wie viel an den Bedingungen hängt.

Weiter unten: der Abschnitt **🔬 Experimente**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktionieren die Bedingungen", expanded=True):
    st.markdown(
        """
1. **Stopp:** Jeder Quader gehört zu einem Stopp von 1 bis m. Bei Stopp 1 wird zuerst entladen. Mit nur einem Stopp gibt es keine Entladereihenfolge.
2. **Entladereihenfolge:** Quader B liegt *über* Quader A (im selben Behälter), wenn sich ihre Grundflächen überlappen und B nicht tiefer beginnt, als A endet. Dann darf der Stopp von B nicht größer sein als der von A: Sonst müsste B erst weggeräumt werden, damit A herauskann. **Geprüft wird nur diese Blockierung von oben**, nicht die seitliche Zufahrt zur Tür.
3. **Stapelbarkeit:** Ein nicht stapelbarer Quader trägt nichts: Über ihm liegt kein Quader, auch keiner, der nur darüber schwebt.
4. **Packer:** Extreme Points mit Projektionen aus Stück 9, auf Wunsch mit der Mindest-Stützfläche 80 % aus Stück 10. Ein Eckpunkt ist nur zulässig, wenn beide Bedingungen gelten. Mit „Bedingungen anwenden: nein“ ignoriert der Packer sie; die Verletzungen werden trotzdem gezählt (rot umrandet).
5. **Schlüssel:** Neben Lieferung, Volumen und Grundfläche gibt es **Stopp ab** (der Quader des letzten Stopps zuerst, er kommt nach unten) und als Gegenprobe **Stopp auf** (das Falsche zuerst).
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Quader**")
    quelle = st.selectbox("Instanz", list(C.QUELLEN), format_func=C.QUELLEN.get, key="quelle_select",
                          help="Die beiden Beispiele haben je zwölf feste Quader mit Stopps und Stapelbarkeit. Die anderen vier sind Zufallsinstanzen mit verschiedener Verteilung der Kanten.")
    n_index = st.selectbox("Zahl der Quader (nur Zufallsinstanzen)", list(range(len(C.N_WERTE))), format_func=lambda i: str(C.N_WERTE[i]), key="n_select", help="Gilt nur für Zufallsinstanzen.")
    seed = st.number_input("Startzahl der Zufallsinstanz", *bounds("seed_input"), key="seed_input", step=1, help="Wirkt nur bei den Zufallsinstanzen.")
    st.button("🎲 Neue Zufallsinstanz würfeln", width="stretch", on_click=randomize_seed)
    st.markdown("**Bedingungen**")
    m_index = st.selectbox("Zahl der Stopps", list(range(len(C.M_WERTE))), format_func=C.M_TEXT.get, key="m_select", help="Auf wie viele Stopps die Quader verteilt sind (zufällig, gleich verteilt).")
    q_index = st.selectbox("Nicht stapelbare Quader", list(range(len(C.Q_WERTE))), format_func=C.Q_TEXT.get, key="q_select", help="Anteil der Quader, über denen nichts liegen darf (zufällig).")
    anwenden = st.selectbox("Bedingungen anwenden", [1, 0], format_func=lambda i: "ja" if i == 1 else "nein (Verletzungen zählen)", key="anwenden_select",
                            help="Bei „nein“ ignoriert der Packer Entladereihenfolge und Stapelbarkeit; die Verletzungen werden gezählt und rot umrandet.")
    st.markdown("**Packen**")
    schluessel = st.selectbox("Sortierschlüssel", list(C.SCHLUESSEL), format_func=C.SCHLUESSEL.get, key="schluessel_select", help="Wonach die Quader sortiert werden.")
    s_index = st.selectbox("Mindest-Stützfläche", list(range(len(C.S_WERTE))), format_func=C.S_TEXT.get, key="smin_select", help="Stück 10: Anteil der Grundfläche, auf dem jeder Quader mindestens aufliegt.")
    st.markdown("**Ansicht**")
    schritt = st.number_input("Schritt (0 = alle Quader)", *bounds("schritt_input"), key="schritt_input", step=1,
                              help="Zeigt den Zustand nach den ersten k Quadern in der Reihenfolge des Schlüssels. Größere Werte als die Zahl der Quader zeigen alle.")
    behaelter = st.number_input("Behälter (der gezeichnet wird)", *bounds("behaelter_input"), key="behaelter_input", step=1, help="Nummer des Behälters, der gezeichnet wird. Gibt es weniger, wird der letzte gezeigt.")
    entladen = st.number_input("Entladen bis Stopp (0 = nichts entladen)", *bounds("entladen_input"), key="entladen_input", step=1,
                               help="Nimmt die Quader der Stopps 1 bis k aus der Zeichnung. Quader, die unter einem später zu entladenden lagen, werden im Verdikt gezählt.")
    farbe = st.selectbox("Farbe der Quader", list(C.FARBEN), format_func=C.FARBEN.get, key="farbe_select", help="Stopp, Stapelbarkeit oder Reihenfolge des Setzens.")

sync_query_params({"quelle_select": int(quelle), "n_select": int(n_index), "seed_input": int(seed), "schluessel_select": int(schluessel), "m_select": int(m_index), "q_select": int(q_index),
                   "smin_select": int(s_index), "anwenden_select": int(anwenden), "schritt_input": int(schritt), "behaelter_input": int(behaelter), "farbe_select": int(farbe), "entladen_input": int(entladen)})

settings = Settings(int(quelle), int(n_index), int(seed), int(schluessel), int(m_index), int(q_index), int(s_index), int(anwenden), int(schritt), int(behaelter), int(farbe), int(entladen))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
m1.metric("Behälter (ganze Packung)", a.count, delta=a.count - a.ohne, delta_color="inverse", help="Delta: Behälterzahl mit den gewählten Einstellungen minus Behälterzahl ohne Entladereihenfolge und Stapelbarkeit (gleicher Schlüssel).")
m2.metric("Ohne Bedingung", a.ohne, delta="Vergleich", delta_color="off")
if a.opt is not None:
    m3.metric("Optimum (ohne Stützbedingung)", a.opt, delta="Referenz (CP-SAT)", delta_color="off")
else:
    m3.metric("Optimum", "nicht berechnet", delta="nur für die Beispiele", delta_color="off")
m4.metric("Untere Schranke", a.schranke, delta="Volumen oder große Quader", delta_color="off")
volumen = sum(w * d * h for w, d, h in a.inst.kisten)
nicht = sum(1 for x in a.stapelbar if not x)
st.caption(f"{a.inst.n} Quader, Gesamtvolumen {volumen} von {a.inst.cap ** 3} je Behälter, {nicht} nicht stapelbar, {max(a.stopp)} Stopps. Kleinste Stützfläche in der ganzen Packung: {100 * a.stuetz_min:.0f} %.")
st.markdown(f"**Zustand nach {a.schritt} von {a.inst.n} Quadern, Behälter {a.gezeigt + 1} von {len(a.bins)}:** der rote Rahmen ist der Behälter"
            + {0: ", die Farbe zeigt die Reihenfolge des Setzens.", 1: ", die Farbe zeigt den Stopp.", 2: ", grün ist stapelbar, rot nicht stapelbar."}[settings.farbe])
markiert = {i for p in A.blockierte_paare(a.inst.kisten, [p for p in a.platz], a.stopp) + A.getragene_paare(a.inst.kisten, [p for p in a.platz], a.stapelbar) for i in p}
st.plotly_chart(build_behaelter(a.inst.kisten, a.platz, a.gezeigt, a.inst.cap, a.zustand[a.gezeigt] if a.zustand else (), settings.farbe, a.stopp, a.stapelbar, markiert), width="stretch", key="main_chart")
if settings.farbe == 1:
    st.caption("Stopp: " + " · ".join(f"Stopp {i + 1} = {f}" for i, f in enumerate(C.STOPP_FARBEN[:max(a.stopp)])) + ". Rot umrandete Quader kommen in einer Verletzung vor. Grüne Rauten: Eckpunkte. Der Behälter lässt sich mit der Maus drehen.")
else:
    st.caption("Rot umrandete Quader kommen in einer Verletzung vor (blockiert oder über einem nicht stapelbaren). Grüne Rauten: Eckpunkte. Der Behälter lässt sich mit der Maus drehen.")
kind, text = verdict_entladen(a)
getattr(st, kind)(text)

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was kosten die Bedingungen, und lohnt es sich, nach dem Stopp zu sortieren?")
kind, text = verdict_aktuell(a)
getattr(st, kind)(text)

zeilen = ["| Schlüssel \\ Bedingung | " + " | ".join(C.BEDINGUNG_KURZ[c] for c in BEDINGUNG_LISTE) + " |", "|---|" + "---|" * len(BEDINGUNG_LISTE)]
for k in SCHLUESSEL_LISTE:
    zeilen.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(str(a.tabelle[k][c]) for c in BEDINGUNG_LISTE) + " |")
st.markdown("Behälterzahl der ganzen Packung für alle 20 Kombinationen (Spalten: ohne Bedingung, nur Entladereihenfolge, nur Stapelbarkeit, beide Bedingungen; mit den gewählten Stopps, dem Anteil nicht stapelbar und der Mindest-Stützfläche; die Schlüssel mit Stopp nutzen immer die echten Stopps):\n\n" + "\n".join(zeilen))
kind, text = verdict_tabelle(a)
getattr(st, kind)(text)

st.markdown("### ⚠️ Was klemmt, wenn man die Bedingungen ignoriert?")
kind, text = verdict_verletzung(a)
getattr(st, kind)(text)
st.caption("Gezählt in der Packung ohne Bedingung (gleicher Schlüssel, gleiche Mindest-Stützfläche) an den Stopps und der Stapelbarkeit dieser Instanz. Betroffen ist jeder Quader, der in mindestens einem Paar vorkommt.")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experimente: Gilt das für viele Instanzen?")
st.caption(
    f"Gemessen an je {C.INSTANZEN} festen Zufallsinstanzen pro Zelle, Behälter {C.CAP} mal {C.CAP} mal {C.CAP}, ganzzahlige Maße der Quader ohne Drehung, Mindest-Stützfläche {round(100 * C.MESS_SMIN)} %. "
    "Die Zahlen sind vorberechnet (`generate_precomputed.py`)."
)
e1, e2 = st.columns(2)
verteilung = e1.selectbox("Verteilung der Quader", list(range(len(C.VERTEILUNGEN))), index=0, format_func=lambda i: C.VERTEILUNGEN[i][1], key="exp_verteilung")
ni = e2.selectbox("Zahl der Quader n", list(range(len(C.MESS_N))), index=1, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
z = zeile(int(verteilung), int(ni))

st.markdown("### Experiment 1: Was kosten die Bedingungen?")
st.plotly_chart(build_messung(z["mittel"], "Behälter über der Schranke (Mittel)"), width="stretch", key="exp_chart")
tab = ["| Schlüssel | ohne | " + " | ".join(C.KOMBI_KURZ) + " |", "|---|---|" + "---|" * len(C.KOMBIS)]
for k in SCHLUESSEL_LISTE:
    tab.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(f"{z['mittel'][k][c]:.2f}" for c in range(len(C.KOMBIS) + 1)) + " |")
st.markdown("\n".join(tab))
st.caption("Mittlere Behälter über der Volumenschranke (Schlüssel in den Zeilen, Bedingung in den Spalten: m Stopps, q Anteil nicht stapelbar), Mittel über die Instanzen der Zelle. Bei 20 bis 80 Quadern fehlt das Optimum, die Schranke ist locker: Lesen Sie die Unterschiede, nicht den Abstand.")
kind, text = verdict_kosten(z)
getattr(st, kind)(text)

st.markdown("### Experiment 2: Lohnt es sich, nach dem Stopp zu sortieren?")
kind, text = verdict_messung(z)
getattr(st, kind)(text)
tab_m = ["| Schlüssel | " + " | ".join(C.KOMBI_KURZ) + " |", "|---|" + "---|" * len(C.KOMBIS)]
for k in SCHLUESSEL_LISTE:
    tab_m.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(str(z["mehr"][k][c]) for c in range(1, len(C.KOMBIS) + 1)) + " |")
st.markdown("\n".join(tab_m))
st.caption(f"Zahl der Instanzen (von {z['instanzen']}), in denen die Bedingung mehr Behälter braucht als ohne (gleicher Schlüssel).")

st.markdown("### Experiment 3: Wie viel würde beim Entladen klemmen?")
tab3 = ["| Bedingung | blockierte Paare je Instanz | Paare über nicht stapelbaren | betroffene Quader |", "|---|---|---|---|"]
for c in range(1, len(C.KOMBIS) + 1):
    v = z["verletzung"][c]
    tab3.append(f"| {C.KOMBI_KURZ[c - 1]} | {v['paare']:.1f} | {v['nicht']:.1f} | {v['quader']:.0f} % |")
st.markdown("\n".join(tab3))
st.caption("In der Packung OHNE Bedingung (Schlüssel Grundfläche, Mindest-Stützfläche 80 %), gemessen an den Stopps und der Stapelbarkeit der Kombination; Mittel je Instanz, Anteil der betroffenen Quader an allen Quadern.")
kind, text = verdict_verletzung_raster(z)
getattr(st, kind)(text)

st.markdown("### Experiment 4: Was bleibt im besten Fall übrig? (Orakel)")
oz = orakel_zeilen()
tab4 = ["| Verteilung, nicht stapelbar | Optimum ohne / mit | Heuristik ohne / mit | mehr | trifft |", "|---|---|---|---|---|"]
for r in oz:
    offen = f", {r['offen']} offen" if r["offen"] else ""
    tab4.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]}, {round(100 * r['q'])} %{offen} | {r['ohne']:.2f} / {r['mit']:.2f} | {r['heur_ohne']:.2f} / {r['heur_mit']:.2f} | {r['mehr']} von {r['entschieden']} | {r['trifft']} |")
st.markdown("\n".join(tab4))
st.caption("Optimum und Heuristik je ohne und mit Bedingungen; mehr = Instanzen, in denen die Bedingungen im Optimum mehr Behälter brauchen; trifft = Instanzen, in denen die Heuristik das Optimum mit Bedingungen erreicht. 12 Quader, 3 Stopps, 40 Instanzen je Verteilung. Optimum mit CP-SAT bei freier Platzierung, **ohne Stützbedingung**; die Heuristik ist der Packer mit Schlüssel Grundfläche, ebenfalls ohne Stützbedingung. Mittel über die entschiedenen Instanzen.")
kind, text = verdict_orakel(oz)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist |
|---|---|
| **Nur die Blockierung von oben** | Ein Quader kann auch seitlich eingeschlossen sein (hinten oder neben der Tür). Das wird nicht geprüft; die Packung kann also beim Entladen mehr umgestaut werden müssen, als die Demo zählt. |
| **Stopps und Stapelbarkeit sind zufällig** | Echte Ladungen haben Stopps, die mit Größe und Gewicht zusammenhängen. Praxisdaten sind nicht gemessen. |
| **Kein Optimum mit Stützbedingung** | Die Stützfläche lässt sich in CP-SAT nicht linear ausdrücken; das Orakel gilt ohne sie und nur bei 12 Quadern. |
| **Kein Gewicht, keine Stapellast** | Ein stapelbarer Quader trägt hier beliebig viel. Tragfähigkeit und Gewichtsgrenzen kommen nicht vor. |
| **Keine Drehung** | Dürfen die Quader gedreht werden, ändert sich die Aufgabe; die Demo misst es nicht. |
| **Das Umstauen beim Entladen wird nicht berechnet** | Wer die Bedingungen ignoriert, muss umstauen. Was das kostet, misst die Umstauen-Linie, nicht diese Demo. |
| **Alle Quader sind vor dem Packen bekannt** | Wer jeden Quader sofort einsortieren muss, kann nicht sortieren. Das ist Online-Packen. Mehr dazu: [Online](https://sebastianhanisch.net/konzepte-online-algorithmen.html). |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Quader mit ganzzahliger Breite, Tiefe und Höhe, einem Stopp und einer Angabe zur Stapelbarkeit, und Behälter der Größe $C \times C \times C$. *Gesucht:* eine überlappungsfreie Platzierung aller Quader in möglichst wenigen Behältern, bei der nichts von oben blockiert und über nicht stapelbaren Quadern nichts liegt.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Quader |
| $w_i$, $d_i$, $h_i$ | Breite, Tiefe und Höhe von Quader $i$ |
| $(x_i, y_i, z_i)$ | linke hintere untere Ecke von Quader $i$ |
| $t_i \in \{1, \dots, m\}$ | Stopp von Quader $i$ (1 wird zuerst entladen) |
| $\sigma_i \in \{0, 1\}$ | 1, wenn Quader $i$ stapelbar ist |
| $C$ | Kantenlänge eines Behälters |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Behältern über alle Platzierungen |

**Über.** Quader $j$ liegt über Quader $i$ (im selben Behälter), $j \succ i$, wenn $z_j \ge z_i + h_i$ und $[x_i, x_i + w_i) \cap [x_j, x_j + w_j) \ne \emptyset$ und $[y_i, y_i + d_i) \cap [y_j, y_j + d_j) \ne \emptyset$.

**Entladereihenfolge.** Für alle Paare im selben Behälter: $j \succ i \Rightarrow t_j \le t_i$. Verletzt ist ein Paar mit $j \succ i$ und $t_j > t_i$ (blockiert): $i$ kann erst nach $j$ entladen werden. Geprüft wird nur das Darüberliegen, nicht die seitliche Zufahrt.

**Stapelbarkeit.** Für alle Paare im selben Behälter: $\sigma_i = 0 \Rightarrow$ es gibt kein $j$ mit $j \succ i$.

**Reihenfolge und Packer.** Wie in Stück 9 und 10; ein Eckpunkt ist nur zulässig, wenn der Quader passt, nichts überlappt, die Stützfläche mindestens $s$ ist und für alle schon gesetzten $k$ gilt: $q \succ k \Rightarrow (t_q \le t_k \wedge \sigma_k = 1)$ und $k \succ q \Rightarrow (t_k \le t_q \wedge \sigma_q = 1)$. Schlüssel: Volumen $w d h$, Grundfläche $w d$, Stopp fallend und dann Grundfläche, Stopp aufsteigend und dann Grundfläche (Gegenprobe).

**Schranken.** $L_{\mathrm{Vol}} = \left\lceil \tfrac{1}{C^3} \sum_i w_i d_i h_i \right\rceil \le \mathrm{OPT}$; $L_{\mathrm{gr}} = |\{ i : w_i, d_i, h_i > C/2 \}| \le \mathrm{OPT}$; $L = \max(L_{\mathrm{Vol}}, L_{\mathrm{gr}})$. Sie gelten ohne die Bedingungen; mit Bedingungen ist das Optimum nicht kleiner.

**Exaktes Optimum** (nur Generator und Tests, nicht diese App). CP-SAT wie in Stück 9; „$j \succ i$“ ist linear ausdrückbar: ein Hilfsbool $a_{ji} \Leftrightarrow z_j \ge z_i + h_i$, und $a_{ji}$ im selben Behälter erzwingt eine der vier Trennungen in $x$ oder $y$ (sonst würden sich die Grundflächen überlappen). Verboten ist $j \succ i$ für jedes Paar mit $t_j > t_i$ oder $\sigma_i = 0$. Die Stützbedingung lässt sich nicht linear ausdrücken und fehlt dort.

**Literatur.** Keine Zahl und keine Aussage der Literatur ist in diese Demo übernommen; alle Zahlen sind selbst gemessen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
