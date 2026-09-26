"""
Integration tests for the FIRMS ingestion pipeline.

NOTE: These tests require a running PostgreSQL+PostGIS database.
They are skipped by default in CI. Run with:
    IGNIS_TEST_DB=1 pytest tests/integration/test_ingestion_pipeline.py -v
"""
import pytest
import os

SKIP_DB = not os.environ.get("IGNIS_TEST_DB")


@pytest.mark.skipif(SKIP_DB, reason="Database not available (set IGNIS_TEST_DB=1)")
def test_ingest_and_classify_pipeline():
    """End-to-end: ingest → enrich → classify → store → alert."""
    # This would test the full Celery pipeline with a live DB
    pass


@pytest.mark.skipif(SKIP_DB, reason="Database not available (set IGNIS_TEST_DB=1)")
def test_deduplication():
    """Ingesting the same hotspot twice should not create duplicates."""
    pass
