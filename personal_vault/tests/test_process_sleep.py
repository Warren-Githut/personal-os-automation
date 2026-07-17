#!/usr/bin/env python3
"""Tests for process_sleep.py - TDD RED phase: duplicate key should be date only."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, "C:/Users/khoans/Documents/Personal_OS/personal_vault/scripts")

from process_sleep import (
    parse_all_sleep_logs,
    parse_duration,
    get_duplicate_key,
    build_entry,
    generate_insight,
    is_duplicate,
)


# ============================================================
# RED PHASE: Write failing tests first
# ============================================================

class TestParseAllSleepLogs:
    """Tests for parse_all_sleep_logs function."""

    def test_parse_single_sleep_log(self):
        """Should parse single health log entry with all fields."""
        content = "Health log june 14: :hospital: Health: 6h50 | quality 92 | 63kg | 17h | Huyết áp: 98/71"
        results = parse_all_sleep_logs(content)
        assert len(results) == 1
        assert results[0]["date"] == "2026-06-14"
        assert results[0]["sleep"] == "6h50"
        assert results[0]["quality"] == "92"
        assert results[0]["weight"] == "63kg"
        assert results[0]["fasting"] == "17h"
        assert results[0]["bp"] == "98/71"

    def test_parse_multiple_sleep_logs_in_one_file(self):
        """Should parse multiple sleep logs from single content."""
        content = """Health log june 14: Health: 6h50 | quality 92 | 63kg | 17h | Huyết áp: 98/71
Health log june 15: Health: 6h50 | quality 88 | 63kg | 17h | Huyết áp: 99/72"""
        results = parse_all_sleep_logs(content)
        assert len(results) == 2
        assert results[0]["date"] == "2026-06-14"
        assert results[1]["date"] == "2026-06-15"

    def test_parse_sleep_log_without_bp(self):
        """Should parse log without blood pressure."""
        content = "Health log june 10: Health: 7h20 | quality 93 | 63kg | 16h"
        results = parse_all_sleep_logs(content)
        assert len(results) == 1
        assert results[0]["bp"] is None
        assert results[0]["sleep"] == "7h20"


class TestParseDuration:
    """Tests for parse_duration function."""

    def test_parse_hours_only(self):
        assert parse_duration("7h") == 7.0

    def test_parse_hours_and_minutes(self):
        assert parse_duration("7h30") == 7.5
        assert parse_duration("6h50") == 6 + 50/60

    def test_case_insensitive(self):
        assert parse_duration("7H30") == 7.5


class TestDuplicateKey:
    """Tests for duplicate key generation - SHOULD BE DATE ONLY."""

    def test_duplicate_key_is_date_only(self):
        """Duplicate key should be date ONLY, not include sleep duration."""
        data = {"date": "2026-06-14", "sleep": "6h50"}
        # KEY CHANGE: duplicate key should be date ONLY
        assert get_duplicate_key(data) == "2026-06-14"

    def test_same_date_different_sleep_same_key(self):
        """Same date with different sleep should produce SAME key."""
        data1 = {"date": "2026-06-14", "sleep": "6h50"}
        data2 = {"date": "2026-06-14", "sleep": "7h30"}
        # Both should have same key (date only)
        assert get_duplicate_key(data1) == get_duplicate_key(data2)
        assert get_duplicate_key(data1) == "2026-06-14"


class TestIsDuplicate:
    """Tests for duplicate detection - SAME DATE = DUPLICATE regardless of sleep."""

    def test_duplicate_detected_same_date_different_sleep(self):
        """Same date with different sleep should be DUPLICATE."""
        log_content = """### 2026-06-14
Sleep: 6h50 | Quality: 92/100"""
        data = {"date": "2026-06-14", "sleep": "7h30", "quality": "95"}
        is_dup, key = is_duplicate(log_content, data)
        assert is_dup is True
        assert key == "2026-06-14"

    def test_duplicate_detected_same_date_same_sleep(self):
        """Same date with same sleep should be DUPLICATE."""
        log_content = """### 2026-06-14
Sleep: 6h50 | Quality: 92/100"""
        data = {"date": "2026-06-14", "sleep": "6h50", "quality": "92"}
        is_dup, key = is_duplicate(log_content, data)
        assert is_dup is True
        assert key == "2026-06-14"

    def test_not_duplicate_different_date(self):
        """Different date should NOT be duplicate."""
        log_content = """### 2026-06-14
Sleep: 6h50 | Quality: 92/100"""
        data = {"date": "2026-06-15", "sleep": "6h50", "quality": "92"}
        is_dup, key = is_duplicate(log_content, data)
        assert is_dup is False


class TestBuildEntry:
    """Tests for build_entry function."""

    def test_build_entry_with_bp(self):
        data = {"date": "2026-06-14", "sleep": "6h50", "quality": "92",
                "weight": "63kg", "fasting": "17h", "bp": "98/71"}
        entry = build_entry(data, "direct_paste")
        assert "### 2026-06-14" in entry
        assert "Sleep: 6h50" in entry
        assert "Quality: 92/100" in entry
        assert "Blood pressure: 98/71" in entry
        assert "direct_paste" in entry

    def test_build_entry_without_bp(self):
        data = {"date": "2026-06-14", "sleep": "6h50", "quality": "92",
                "weight": "63kg", "fasting": "17h", "bp": None}
        entry = build_entry(data, "test_source")
        assert "Blood pressure" not in entry


class TestGenerateInsight:
    """Tests for generate_insight function."""

    def test_sleep_below_baseline(self):
        data = {"sleep": "6h50", "quality": "92", "bp": "98/71",
                "weight": "63kg", "fasting": "17h"}
        insight = generate_insight({"sleep": "6h50", "quality": "92", "bp": "98/71",
                "weight": "63kg", "fasting": "17h"})
        # Should mention sleep below baseline
        assert "thấp hơn baseline 7h" in insight

    def test_sleep_at_baseline(self):
        insight = generate_insight({"sleep": "7h30", "quality": "95", "bp": "100/70",
                "weight": "63kg", "fasting": "16h"})
        assert "đạt baseline" in insight

    def test_high_bp_flagged(self):
        insight = generate_insight({"sleep": "7h00", "quality": "90", "bp": "150/95",
                "weight": "63kg", "fasting": "16h"})
        assert "cao" in insight.lower()

    def test_low_bp_flagged(self):
        insight = generate_insight({"sleep": "7h00", "quality": "90", "bp": "85/55",
                "weight": "63kg", "fasting": "16h"})
        assert "thấp" in insight.lower()

    def test_normal_bp(self):
        insight = generate_insight({"sleep": "7h00", "quality": "90", "bp": "120/80",
                "weight": "63kg", "fasting": "16h"})
        assert "bình thường" in insight.lower()


if __name__ == "__main__":
    # Run tests to verify they fail (RED phase)
    pytest.main([__file__, "-v"])