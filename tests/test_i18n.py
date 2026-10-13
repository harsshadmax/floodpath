"""T-27 to T-32 (blueprint Section 10.3): dictionary parity, placeholders, formatting, fallback."""
import pytest

from src import i18n

LANGS = ("en", "ta", "hi")


def keys(lang):
    return {k for k in i18n.load_dictionary(lang) if k != "_meta"}


def test_t27_key_parity():
    base = keys("en")
    assert len(base) > 50
    for lang in ("ta", "hi"):
        assert keys(lang) == base, f"{lang} differs from en: {sorted(keys(lang) ^ base)[:5]}"


def test_t28_placeholder_parity():
    en = i18n.load_dictionary("en")
    for lang in ("ta", "hi"):
        d = i18n.load_dictionary(lang)
        for key in keys("en"):
            assert i18n.placeholders(d[key]) == i18n.placeholders(en[key]), f"{lang}:{key}"


def test_t29_completeness_and_critical_keys():
    for lang in LANGS:
        d = i18n.load_dictionary(lang)
        for key in keys(lang):
            assert d[key].strip(), f"empty string {lang}:{key}"
            assert "|" not in d[key], f"pipe character in {lang}:{key}"
            assert "<" not in d[key] and ">" not in d[key], f"raw HTML in {lang}:{key}"
        for key in i18n.CRITICAL_KEYS:
            assert key in d, f"critical key {key} missing in {lang}"
        for prefix in i18n.CRITICAL_PREFIXES:
            assert any(k.startswith(prefix) for k in d), f"no {prefix}* keys in {lang}"


def test_meta_blocks_and_draft_status():
    assert i18n.load_dictionary("en")["_meta"]["language"] == "en"
    for lang in ("ta", "hi"):
        meta = i18n.load_dictionary(lang)["_meta"]
        assert meta["language"] == lang
        assert meta["status"] == "draft"  # blueprint I18N-13: stays draft until a reviewer signs off


def test_banner_keeps_simulation_wording():
    # Claims policy (blueprint 0.5): the banner must carry the simulation meaning in every language.
    assert "simulat" in i18n.t("banner.simulation", "en").lower()
    assert "உருவகப்படுத்த" in i18n.t("banner.simulation", "ta")
    assert "सिमुलेशन" in i18n.t("banner.simulation", "hi")


def test_t31_number_formatting():
    assert i18n.fmt_int(1234567) == "12,34,567"
    assert i18n.fmt_int(999) == "999"
    assert i18n.fmt_int(1000) == "1,000"
    assert i18n.fmt_int(100000) == "1,00,000"
    assert i18n.fmt_int(-1234567) == "-12,34,567"
    assert i18n.fmt_int(0) == "0"
    assert i18n.fmt_pct(0.1234) == "12.3%"
    assert i18n.fmt_pct(1) == "100.0%"


def test_t32_missing_key_falls_back_to_english(monkeypatch):
    real = i18n.load_dictionary

    def fake(lang):
        data = dict(real(lang))
        if lang == "ta":
            data.pop("nav.overview", None)
        return data

    monkeypatch.setattr(i18n, "load_dictionary", fake)
    i18n.drain_warnings()
    assert i18n.t("nav.overview", "ta") == real("en")["nav.overview"]
    assert "I18N_KEY_MISSING" in i18n.drain_warnings()


def test_t32_unknown_key_returns_key_and_unsupported_language_uses_english():
    i18n.drain_warnings()
    assert i18n.t("no.such.key", "en") == "no.such.key"
    assert i18n.t("nav.overview", "fr") == i18n.load_dictionary("en")["nav.overview"]
    codes = i18n.drain_warnings()
    assert "I18N_KEY_MISSING" in codes and "I18N_LANGUAGE_UNSUPPORTED" in codes


def test_placeholders_are_filled_and_missing_params_raise():
    out = i18n.t("expl.unreachable_all", "hi", scenario="X")
    assert "X" in out and "{" not in out
    with pytest.raises(i18n.I18NParamError):
        i18n.t("expl.unreachable_all", "en")


def test_escape_html():
    assert i18n.escape_html("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert i18n.escape_html('A & "B"') == "A &amp; &quot;B&quot;"
