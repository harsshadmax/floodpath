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
        {"ROBUSTNESS_SHARE_RANGE": (0.5, 0.1)},
        {"N_ORIGINS": 5, "MIN_ORIGINS": 10},
        {"MAX_SNAP_DISTANCE_M": -1},
        {"DEFAULT_LANGUAGE": "fr"},
    ],
)
def test_invalid_values_are_rejected(overrides):
    with pytest.raises(ConfigError):
        validate_config(replace(CONFIG, **overrides))


def test_scenario_shares_must_not_decrease_or_exceed_one():
    for bad in ((("mild", 0.5), ("moderate", 0.2), ("severe", 0.35)),
                (("mild", 0.1), ("moderate", 0.2), ("severe", 1.5))):
        with pytest.raises(ConfigError):
            validate_config(replace(CONFIG, SCENARIO_FEATURE_SHARE=bad))


def test_scenario_names_must_be_in_order():
    bad = (("moderate", 0.2), ("mild", 0.1), ("severe", 0.35))
    with pytest.raises(ConfigError):
        validate_config(replace(CONFIG, SCENARIO_FEATURE_SHARE=bad))


def test_study_zone_is_set_and_valid():
    assert isinstance(CONFIG, Config)
    assert CONFIG.STUDY_AREA and CONFIG.STUDY_BBOX
    w, s, e, n = CONFIG.STUDY_BBOX
    assert w < e and s < n
    validate_config(CONFIG, require_study_area=True)


def test_study_area_required_only_when_asked():
    unset = replace(CONFIG, STUDY_AREA=None, STUDY_BBOX=None)
    validate_config(unset)  # allowed until the road graph is built
    with pytest.raises(ConfigError) as err:
        validate_config(unset, require_study_area=True)
    assert err.value.key == "STUDY_BBOX"


@pytest.mark.parametrize(
    "bbox",
    [
        (80.27, 13.01, 80.205, 13.10),  # west after east
        (80.205, 13.10, 80.27, 13.01),  # south after north
        (70.0, 13.0, 71.0, 13.1),  # outside the Chennai region
    ],
)
def test_bad_study_bbox_rejected(bbox):
    with pytest.raises(ConfigError) as err:
        validate_config(replace(CONFIG, STUDY_BBOX=bbox))
    assert err.value.key == "STUDY_BBOX"


def test_line_buffer_must_be_positive():
    with pytest.raises(ConfigError):
        validate_config(replace(CONFIG, LINE_BUFFER_M=0))
