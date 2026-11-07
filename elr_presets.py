"""Permalink (Begrenzen), Presets und Zufalls-Seed-Button (Standardmuster aus dem Demo-Portfolio)."""

import random
from dataclasses import dataclass

import streamlit as st

import elr_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None


SETTING_SPECS = {
    "quelle_select": SettingSpec("src", int, 0, 0, max(C.QUELLEN)),
    "n_select": SettingSpec("n", int, 0, 0, len(C.N_WERTE) - 1),
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
    "schluessel_select": SettingSpec("key", int, C.GRUNDFLAECHE, 0, max(C.SCHLUESSEL)),
    "m_select": SettingSpec("m", int, 2, 0, len(C.M_WERTE) - 1),
    "q_select": SettingSpec("q", int, 1, 0, len(C.Q_WERTE) - 1),
    "smin_select": SettingSpec("smin", int, 1, 0, len(C.S_WERTE) - 1),
    "anwenden_select": SettingSpec("apply", int, 1, 0, 1),
    "schritt_input": SettingSpec("step", int, 0, 0, 200),
    "behaelter_input": SettingSpec("bin", int, 1, 1, 50),
    "farbe_select": SettingSpec("color", int, 1, 0, max(C.FARBEN)),
    "entladen_input": SettingSpec("unload", int, 0, 0, C.ENTLADEN_MAX),
}
PRESET_KEYS = {"quelle": "quelle_select", "n_index": "n_select", "seed": "seed_input", "schluessel": "schluessel_select", "m_index": "m_select", "q_index": "q_select", "s_index": "smin_select",
               "anwenden": "anwenden_select", "schritt": "schritt_input", "behaelter": "behaelter_input", "farbe": "farbe_select", "entladen": "entladen_input"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
            except (ValueError, TypeError):
                continue
            if spec.lo is not None:
                value = max(spec.lo, value)
            if spec.hi is not None:
                value = min(spec.hi, value)
            st.session_state[state_key] = value
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][key]


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Preset ohne Eintrag für einen Regler meint dessen
    Standardwert) mit dem Session State. Ein später ergänzter Regler braucht nur seinen Eintrag in SETTING_SPECS,
    dann hebt auch seine Änderung die Markierung auf (tests/test_layout.py prüft das für jeden Regler)."""
    preset_key_of = {state_key: key for key, state_key in PRESET_KEYS.items()}
    for name, preset in C.PRESETS.items():
        if all(
            st.session_state.get(state_key, spec.default) == preset.get(preset_key_of.get(state_key), spec.default)
            for state_key, spec in SETTING_SPECS.items()
        ):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden:")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seed():
    """Neue Startzahl und, falls noch ein Handbeispiel gewählt ist, eine Zufallsinstanz mit mittleren Quadern: die Startzahl wirkt nur dort, ein Würfeln ohne sichtbare Wirkung gäbe es sonst."""
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)
    if st.session_state.get("quelle_select", 0) in C.BEISPIELE:
        st.session_state["quelle_select"] = C.ZUFALL_QUELLEN[0]
