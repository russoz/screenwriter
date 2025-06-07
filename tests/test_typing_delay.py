# (C) 2025 Alexei Znamensky
# Licensed under the GPL-3.0-or-later license. See LICENSES/GPL-3.0-or-later.txt for details.
# SPDX-FileCopyrightText: 2025 Alexei Znamensky
# SPDX-License-Identifier: GPL-3.0-or-later
from screenwriter.__main__ import ScreenwriterRunner


def test_typing_delay_returns_float():
    """Test that typing_delay returns a float value."""
    runner = ScreenwriterRunner()
    delay = runner.typing_delay()
    assert isinstance(delay, float)
    assert delay > 0


def test_typing_delay_within_reasonable_range():
    """Test that typing delay is within a reasonable range."""
    runner = ScreenwriterRunner()
    delay = runner.typing_delay()
    # Should be at least the minimum delay (0.03) and not too large
    assert 0.03 <= delay <= 1.0
