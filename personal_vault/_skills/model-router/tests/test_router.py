#!/usr/bin/env python3
"""
Smoke tests for Model Router.
Tests: quota, router decision, commands, Pro API connectivity.
"""

import json
import os
import sys
import tempfile
import unittest

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_PARENT = os.path.join(_SCRIPTS_DIR, "..", "scripts")
sys.path.insert(0, _SCRIPTS_PARENT)

# Remove any existing state files to start clean
for f in os.listdir(_SCRIPTS_PARENT):
    if f.endswith("_state.json"):
        os.remove(os.path.join(_SCRIPTS_PARENT, f))

import quota
import router


class TestQuota(unittest.TestCase):

    def setUp(self):
        if os.path.exists(quota.STATE_FILE):
            os.remove(quota.STATE_FILE)

    def test_initial_state(self):
        s = quota.load_state()
        self.assertEqual(s["total_calls"], 0)
        self.assertEqual(s["pro_calls"], 0)
        self.assertEqual(s["pro_pct"], 0.0)

    def test_increment_flash(self):
        s = quota.increment_flash()
        self.assertEqual(s["total_calls"], 1)
        self.assertEqual(s["pro_calls"], 0)
        self.assertEqual(s["pro_pct"], 0.0)

    def test_increment_pro(self):
        s = quota.increment_pro()
        self.assertEqual(s["total_calls"], 1)
        self.assertEqual(s["pro_calls"], 1)
        self.assertEqual(s["pro_pct"], 100.0)

    def test_quota_hit_exact(self):
        for _ in range(90):
            quota.increment_flash()
        for _ in range(10):
            quota.increment_pro()
        s = quota.load_state()
        self.assertEqual(s["pro_pct"], 10.0)
        q = quota.check_quota(s)
        self.assertFalse(q["can_use_pro"])
        self.assertTrue(q["hit_limit"])

    def test_quota_below_limit(self):
        for _ in range(95):
            quota.increment_flash()
        for _ in range(5):
            quota.increment_pro()
        q = quota.check_quota()
        self.assertTrue(q["can_use_pro"])
        self.assertFalse(q["hit_limit"])

    def test_near_warning(self):
        for _ in range(92):
            quota.increment_flash()
        for _ in range(8):
            quota.increment_pro()
        q = quota.check_quota()
        self.assertTrue(q["near_warning"])
        self.assertTrue(q["can_use_pro"])

    def test_override(self):
        for _ in range(90):
            quota.increment_flash()
        for _ in range(10):
            quota.increment_pro()
        q1 = quota.check_quota()
        self.assertFalse(q1["can_use_pro"])
        quota.override_quota()
        q2 = quota.check_quota()
        self.assertTrue(q2["can_use_pro"])

    def test_monthly_reset(self):
        s = quota.load_state()
        s["total_calls"] = 500
        s["pro_calls"] = 50
        s["pro_pct"] = 10.0
        s["month"] = "2020-01"
        quota.save_state(s)
        s2 = quota.load_state()
        self.assertEqual(s2["total_calls"], 0)
        self.assertEqual(s2["month"], quota.get_current_month())

    def test_report_line(self):
        for _ in range(92):
            quota.increment_flash()
        for _ in range(8):
            quota.increment_pro()
        line = quota.report_line()
        self.assertIn("8.0%", line)
        self.assertIn("Model Router", line)


class TestRouter(unittest.TestCase):

    def setUp(self):
        for f in [quota.STATE_FILE, router.STATE_FILE]:
            if os.path.exists(f):
                os.remove(f)

    def test_simple_task_flash(self):
        result = router.decide("xin chào")
        self.assertEqual(result["model"], "flash")

    def test_factual_accuracy_pro(self):
        result = router.decide("cho tôi số liệu doanh thu và COL của LU3 tuần này")
        self.assertEqual(result["model"], "pro")
        self.assertEqual(result["trigger"], "factual_accuracy")
        self.assertTrue(result["needs_factual"])

    def test_tool_chain_depth_trigger(self):
        result = router.decide(
            "phân tích dữ liệu, so sánh với tháng trước, search trong vault, "
            "đọc file báo cáo, và tính toán thống kê"
        )
        self.assertEqual(result["model"], "pro")
        self.assertEqual(result["trigger"], "tool_chain")

    def test_flash_failure_retry(self):
        result = router.decide("xin chào", retry_count=1)
        self.assertEqual(result["model"], "pro")
        self.assertEqual(result["trigger"], "flash_failure")

    def test_router_disabled(self):
        state = router.get_router_state()
        state["enabled"] = False
        router.save_router_state(state)
        result = router.decide("cho tôi số liệu COL")
        self.assertEqual(result["model"], "flash")
        self.assertEqual(result["reason"], "Router disabled via /model-router off")

    def test_quota_block(self):
        for _ in range(90):
            quota.increment_flash()
        for _ in range(10):
            quota.increment_pro()
        result = router.decide("phân tích dữ liệu phức tạp")
        self.assertEqual(result["model"], "flash")
        self.assertEqual(result["trigger"], "quota_hit")


class TestCommands(unittest.TestCase):

    def setUp(self):
        for f in [quota.STATE_FILE, router.STATE_FILE]:
            if os.path.exists(f):
                os.remove(f)
        import importlib
        global cmds
        import commands
        cmds = commands
        importlib.reload(cmds)

    def test_cmd_on_off(self):
        out_off = cmds.cmd_off()
        self.assertIn("⛔", out_off)
        out_on = cmds.cmd_on()
        self.assertIn("✅", out_on)

    def test_cmd_status(self):
        out = cmds.cmd_status()
        self.assertIn("Model Router Status", out)
        self.assertIn("Quota", out)

    def test_cmd_override(self):
        out = cmds.cmd_override()
        self.assertIn("Override", out)
        self.assertIn("20", out)

    def test_cmd_reset(self):
        out = cmds.cmd_reset()
        self.assertIn("0%", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
