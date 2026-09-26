"""
API tests for analytics schemas.
"""
import pytest
from app.schemas.spatial import AnalyticsSummaryResponse, ClassificationCount, TimelineDataPoint
from app.models.spatial import MLClassificationEnum


def test_analytics_summary_schema():
    """AnalyticsSummaryResponse should hold the 4 dashboard stat values."""
    summary = AnalyticsSummaryResponse(
        total_hotspots=12500,
        active_industrial_fires=23,
        high_severity_alerts=7,
        unverified_classifications=890,
    )
    assert summary.total_hotspots == 12500
    assert summary.high_severity_alerts == 7


def test_classification_count_schema():
    """ClassificationCount should bind label enum to an integer count."""
    cc = ClassificationCount(label=MLClassificationEnum.GAS_FLARE, count=450)
    assert cc.label == MLClassificationEnum.GAS_FLARE
    assert cc.count == 450


def test_timeline_datapoint():
    """TimelineDataPoint is a date string + count."""
    tp = TimelineDataPoint(date="2024-06-15", count=34)
    assert tp.date == "2024-06-15"
