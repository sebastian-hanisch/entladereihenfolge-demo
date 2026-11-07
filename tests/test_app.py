"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, stellt jede Auswahl
auf jeden ihrer Werte und die Zahlenfelder an ihre Grenzen und prüft, dass kein Python-Fehler auftritt (insbesondere `StreamlitDuplicateElementId`
bei mehreren Diagrammen ohne key= und `StreamlitAPIException` bei Auswahlen mit ungültigem Wert)."""

import os

from streamlit.testing.v1 import AppTest

import elr_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
WUERFEL = "🎲 Neue Zufallsinstanz würfeln"


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texte(at):
    return [e.value for e in at.info] + [e.value for e in at.success] + [e.value for e in at.warning]


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_selectbox_value_does_not_raise():
    keys = [s.key for s in _fresh_app().selectbox]
    erwartet = {"quelle_select", "n_select", "m_select", "q_select", "anwenden_select", "schluessel_select", "smin_select", "farbe_select", "exp_verteilung", "exp_n"}
    assert erwartet <= set(keys)
    werte = {"quelle_select": list(C.QUELLEN), "n_select": list(range(len(C.N_WERTE))), "m_select": list(range(len(C.M_WERTE))), "q_select": list(range(len(C.Q_WERTE))), "anwenden_select": [0, 1],
             "schluessel_select": list(C.SCHLUESSEL), "smin_select": list(range(len(C.S_WERTE))), "farbe_select": list(C.FARBEN), "exp_verteilung": list(range(len(C.VERTEILUNGEN))),
             "exp_n": list(range(len(C.MESS_N)))}
    for key in keys:
        for wert in werte[key]:
            at = _fresh_app()
            at.selectbox(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_zahlenfelder_an_ihren_grenzen_loesen_keinen_fehler_aus():
    for quelle in (0, 5):
        for wert in (0, C.SEED_MAX):
            at = _fresh_app()
            at.selectbox(key="quelle_select").set_value(quelle).run(timeout=TIMEOUT)
            at.number_input(key="seed_input").set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (quelle, wert, [str(e) for e in at.exception])
    for key, werte in (("schritt_input", (0, 1, 5, 12, 13, 200)), ("behaelter_input", (1, 2, 50)), ("entladen_input", tuple(range(C.ENTLADEN_MAX + 1)))):
        for wert in werte:
            at = _fresh_app()
            at.number_input(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_wuerfeln_wechselt_vom_beispiel_zu_einer_zufallsinstanz():
    at = _fresh_app()
    assert at.selectbox(key="quelle_select").value == 0
    at.button[[b.label for b in at.button].index(WUERFEL)].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == 2 and not at.exception
    at.selectbox(key="quelle_select").set_value(5).run(timeout=TIMEOUT)
    seed_vorher = at.number_input(key="seed_input").value
    at.button[[b.label for b in at.button].index(WUERFEL)].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == 5 and at.number_input(key="seed_input").value != seed_vorher


def test_standardansicht_zeigt_das_erwartete_verdikt():
    at = _fresh_app()
    assert any("Nach der Grundfläche sortiert und mit 3 Stopps und 20 % nicht stapelbar gesetzt brauchen die Quader **1** Behälter, ohne Bedingung 1. Die Bedingungen kosten hier nichts." in t for t in _texte(at))
    assert any("Mit beiden Bedingungen braucht Stopp ab **2** Behälter, Stopp auf (Gegenprobe) 2, die Grundfläche ohne Rücksicht auf den Stopp 1." in t for t in _texte(at))


def test_volumen_kostet_einen_behaelter_und_ignorieren_zeigt_die_verletzungen():
    at = _fresh_app()
    at.selectbox(key="schluessel_select").set_value(C.VOLUMEN).run(timeout=TIMEOUT)
    assert any("brauchen die Quader **2** Behälter, ohne Bedingung 1. Die Bedingungen kosten hier 1." in t for t in _texte(at))
    at.selectbox(key="anwenden_select").set_value(0).run(timeout=TIMEOUT)
    assert not at.exception and any("ohne Beachtung der Bedingungen brauchen die Quader **1** Behälter" in t for t in _texte(at))
    assert any("blockieren **1** Paare" in t and "1 Paare liegen über nicht stapelbaren" in t and "**4** von 12 Quadern sind betroffen" in t for t in _texte(at))


def test_entladen_regler_zeigt_die_blockierten_quader():
    at = _fresh_app()
    at.selectbox(key="quelle_select").set_value(1).run(timeout=TIMEOUT)
    at.selectbox(key="schluessel_select").set_value(C.VOLUMEN).run(timeout=TIMEOUT)
    at.selectbox(key="anwenden_select").set_value(0).run(timeout=TIMEOUT)
    at.number_input(key="entladen_input").set_value(1).run(timeout=TIMEOUT)
    assert not at.exception and any("Nach dem Entladen der Stopps 1 bis 1 sind **4** von 12 Quadern entladen. **2** davon lagen unter einem später zu entladenden Quader" in t for t in _texte(at))
    assert any("blockieren **4** Paare" in t and "**8** von 12 Quadern sind betroffen" in t for t in _texte(at))
    at.selectbox(key="anwenden_select").set_value(1).run(timeout=TIMEOUT)
    assert any("Keiner davon lag unter einem Quader, der später entladen wird" in t for t in _texte(at))


def test_schritt_und_behaelter_regler_halten_ihre_grenzen():
    at = _fresh_app()
    for wert, erwartet in ((0, 12), (1, 1), (5, 5), (12, 12), (13, 12), (200, 12)):
        at.number_input(key="schritt_input").set_value(wert).run(timeout=TIMEOUT)
        assert not at.exception, (wert, [str(e) for e in at.exception])
        assert any(f"Zustand nach {erwartet} von 12 Quadern" in m.value for m in at.markdown), wert
    at.number_input(key="schritt_input").set_value(0).run(timeout=TIMEOUT)
    at.selectbox(key="schluessel_select").set_value(C.VOLUMEN).run(timeout=TIMEOUT)             # Volumen: zwei Behälter
    for wert, erwartet in ((1, 1), (2, 2), (3, 2), (50, 2)):
        at.number_input(key="behaelter_input").set_value(wert).run(timeout=TIMEOUT)
        assert any(f"Behälter {erwartet} von 2:" in m.value for m in at.markdown), wert


def test_expander_und_experimente_stehen_unter_ihren_namen():
    at = _fresh_app()
    labels = [e.label for e in at.expander]
    assert "📐 Mathematische Formulierung" in labels and "⚠️ Annahmen, Grenzen und bekannte Probleme" in labels
    markdown = [m.value for m in at.markdown]
    for titel in ("### Experiment 1: Was kosten die Bedingungen?", "### Experiment 2: Lohnt es sich, nach dem Stopp zu sortieren?", "### Experiment 3: Wie viel würde beim Entladen klemmen?",
                  "### Experiment 4: Was bleibt im besten Fall übrig? (Orakel)"):
        assert any(titel in m for m in markdown), titel
