"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen, jeder Hilfetext stimmt mit der Rechnung überein."""

import elr_algorithm as A
import elr_constants as C
import elr_evaluation as ev
import elr_presets as P

FELDER = ("quelle", "n_index", "seed", "schluessel", "m_index", "q_index", "s_index", "anwenden", "schritt", "behaelter", "farbe", "entladen")


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_widget_bounds():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_defaults_of_the_widgets_equal_the_default_settings():
    s = ev.Settings()
    schluessel = ("quelle_select", "n_select", "seed_input", "schluessel_select", "m_select", "q_select", "smin_select", "anwenden_select", "schritt_input", "behaelter_input", "farbe_select", "entladen_input")
    assert [P.SETTING_SPECS[k].default for k in schluessel] == [getattr(s, f) for f in FELDER]


def _a(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_presets_behaupten_nur_was_stimmt():
    eins = _a("Beispiel 1, Grundfläche, 3 Stopps, 20 % nicht stapelbar")
    assert eins.count == 1 == eins.ohne == eins.opt and "bleibt es bei einem Behälter, dem Optimum" in C.PRESET_HELP["Beispiel 1, Grundfläche, 3 Stopps, 20 % nicht stapelbar"]
    assert eins.settings.farbe == 1 and "Die Farbe zeigt den Stopp" in C.PRESET_HELP["Beispiel 1, Grundfläche, 3 Stopps, 20 % nicht stapelbar"]
    zwei = _a("Beispiel 1, Volumen, 3 Stopps, 20 % nicht stapelbar")
    assert zwei.count == 2 and zwei.ohne == 1 and zwei.tabelle[C.GRUNDFLAECHE][3] == 1 and "sind es zwei Behälter statt einem. Die Grundfläche bleibt bei einem." in C.PRESET_HELP["Beispiel 1, Volumen, 3 Stopps, 20 % nicht stapelbar"]
    drei = _a("Beispiel 2, Volumen, Bedingungen ignoriert, Entladen bis Stopp 1")
    assert drei.count == 1 and drei.settings.anwenden == 0 and drei.verletzung == (4, 0, 8) and (drei.entladen_zahl, drei.entladen_blockiert) == (4, 2)
    hilfe = C.PRESET_HELP["Beispiel 2, Volumen, Bedingungen ignoriert, Entladen bis Stopp 1"]
    assert "Sie passen in einen Behälter, aber vier Paare blockieren, und von den vier Quadern des ersten Stopps lagen zwei unter einem später zu entladenden" in hilfe
    vier = _a("Beispiel 2, Grundfläche, 3 Stopps, 20 % nicht stapelbar")
    assert vier.count == 2 and vier.ohne == 1 and vier.opt == 1 and list(vier.tabelle[C.GRUNDFLAECHE]) == [1, 1, 1, 2]
    assert "Weder die Entladereihenfolge allein noch die Stapelbarkeit allein kostet bei diesen Quadern einen Behälter, beide zusammen kosten einen, obwohl das Optimum bei einem liegt." in C.PRESET_HELP["Beispiel 2, Grundfläche, 3 Stopps, 20 % nicht stapelbar"]
    fuenf = _a("Flache Quader, 40 Stück, 3 Stopps, 20 % nicht stapelbar")
    assert (fuenf.count, fuenf.ohne, fuenf.schranke, fuenf.inst.n) == (7, 5, 2, 40)
    assert "sieben Behälter statt fünf (Schranke 2)" in C.PRESET_HELP["Flache Quader, 40 Stück, 3 Stopps, 20 % nicht stapelbar"]
    for x in (eins, zwei, vier, fuenf):
        assert x.verletzung == (0, 0, 0) and A.gueltig(x.inst.kisten, A.pack(x.inst.kisten, x.stopp, x.stapelbar, list(x.order), x.inst.cap, ev.s_min(x.settings))[1], x.stopp, x.stapelbar)


def test_beispiel_1_nur_die_grundflaeche_bleibt_bei_einem_behaelter():
    """Die Aussage „nur die Grundfläche bleibt bei einem Behälter“ im Handbeispiel: unter allen fünf Schlüsseln braucht nur sie mit beiden Bedingungen einen."""
    a = _a("Beispiel 1, Volumen, 3 Stopps, 20 % nicht stapelbar")
    assert [k for k in range(5) if a.tabelle[k][3] == 1] == [C.GRUNDFLAECHE]
