"""T-16 and related config validation (blueprint Sections 10.3, 12.1)."""
from dataclasses import replace

import pytest

from config import CONFIG, Config, ConfigError, validate_config


def test_default_config_is_valid():
    assert validate_config(CONFIG) is CONFIG


def test_t16_at_risk_must_be_below_blocked():
    with pytest.raises(ConfigError) as err:
        validate_config(replace(CONFIG, FLOOD_FRACTION_AT_RISK=0.5, FLOOD_FRACTION_BLOCKED=0.5))
    assert err.value.code == "CONFIG_INVALID"
    assert err.value.key == "FLOOD_FRACTION_AT_RISK"


def test_t16_at_risk_reversed_order_rejected():
    with pytest.raises(ConfigError):
        validate_config(replace(CONFIG, FLOOD_FRACTION_AT_RISK=0.6, FLOOD_FRACTION_BLOCKED=0.4))


@pytest.mark.parametrize(
    "overrides",
    [
        {"FLOOD_FRACTION_AT_RISK": 0.0},
        {"FLOOD_FRACTION_BLOCKED": 1.5},
        {"AT_RISK_TIME_MULTIPLIER": 0.5},
        {"POINT_BUFFER_M": 0},
        {"COVERAGE_THRESHOLD_MIN": 0},
        {"ROBUSTNESS_RUNS": 0},
        {"ROBUSTNESS_BUFFER_RANGE_M": (50.0, -50.0)},
        {"N_ORIGINS": 5, "MIN_ORIGINS": 10},
        {"MAX_SNAP_DISTANCE_M": -1},
        {"DEFAULT_LANGUAGE": "fr"},
    ],
)
def test_invalid_values_are_rejected(overrides):
    with pytest.raises(ConfigError):
        validate_config(replace(CONFIG, **overrides))


def test_scenario_buffers_must_not_decrease():
    bad = (("mild", 100.0), ("moderate", 0.0), ("severe", 150.0))
    with pytest.raises(ConfigError):
        validate_config(replace(CONFIG, SCENARIO_BUFFER_M=bad))


def test_scenario_names_must_be_in_order():
    bad = (("moderate", 0.0), ("mild", -100.0), ("severe", 150.0))
    with pytest.raises(ConfigError):
        validate_config(replace(CONFIG, SCENARIO_BUFFER_M=bad))


def test_study_area_required_only_when_asked():
    assert isinstance(CONFIG, Config)
    assert CONFIG.STUDY_AREA is None
    validate_config(CONFIG)  # fine in PHASE 0
    with pytest.raises(ConfigError) as err:
        validate_config(CONFIG, require_study_area=True)
    assert err.value.key == "STUDY_AREA"
