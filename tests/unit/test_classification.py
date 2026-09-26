"""
Unit tests for backend/app/ml/model.py — Classification and model loading.
"""
import pytest
from app.models.spatial import MLClassificationEnum


def test_classification_enum_has_six_classes():
    """The MLClassificationEnum must have exactly 6 values per §3.2."""
    values = list(MLClassificationEnum)
    assert len(values) == 6, f"Expected 6 classes, got {len(values)}"


def test_classification_enum_values():
    """Enum values must match the spec class names."""
    expected = {
        "Industrial Fire",
        "Forest Fire",
        "Gas Flare",
        "Agricultural Burn",
        "Mining/Thermal",
        "Unclassified",
    }
    actual = {e.value for e in MLClassificationEnum}
    assert actual == expected, f"Enum mismatch: {actual.symmetric_difference(expected)}"


def test_label_to_enum_mapping():
    """model.py LABEL_TO_ENUM must cover all 6 classes."""
    from app.ml.model import LABEL_TO_ENUM
    assert len(LABEL_TO_ENUM) == 6
    assert all(isinstance(v, MLClassificationEnum) for v in LABEL_TO_ENUM.values())
