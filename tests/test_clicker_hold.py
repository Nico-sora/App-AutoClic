"""Tests for clicker hold mode — no UI needed."""
import time
import threading
from unittest.mock import MagicMock, patch, call
import pytest


def test_hold_mouse_presses_and_releases():
    """Hold mode should press once before loop and release once on stop."""
    with patch("src.core.clicker.MouseController") as MockMouse, \
         patch("src.core.clicker.KbController"):
        mock_mouse = MagicMock()
        MockMouse.return_value = mock_mouse

        from src.core.clicker import Clicker
        c = Clicker()
        c.start(button="left", click_type="hold", interval_ms=50, duration_ms=0)
        time.sleep(0.15)
        c.stop()
        time.sleep(0.1)

        mock_mouse.press.assert_called_once()
        mock_mouse.release.assert_called_once()
        # click() must NOT have been called
        mock_mouse.click.assert_not_called()


def test_hold_does_not_increment_click_count_per_interval():
    """Hold mode click_count stays at 0 (no repeated clicks)."""
    with patch("src.core.clicker.MouseController"), \
         patch("src.core.clicker.KbController"):
        from src.core.clicker import Clicker
        c = Clicker()
        c.start(button="left", click_type="hold", interval_ms=30, duration_ms=0)
        time.sleep(0.15)
        c.stop()
        time.sleep(0.1)
        assert c.click_count == 0


def test_normal_single_click_still_works():
    """Regression: single click type should still call mouse.click."""
    with patch("src.core.clicker.MouseController") as MockMouse, \
         patch("src.core.clicker.KbController"):
        mock_mouse = MagicMock()
        MockMouse.return_value = mock_mouse

        from src.core.clicker import Clicker
        c = Clicker()
        c.start(button="left", click_type="single", interval_ms=30, duration_ms=120)
        time.sleep(0.25)
        c.stop()
        time.sleep(0.1)

        assert mock_mouse.click.call_count >= 2
        mock_mouse.press.assert_not_called()
