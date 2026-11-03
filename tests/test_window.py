import re
import unittest
from pathlib import Path

from halloween_hub.window import WaylandWindows, WINDOW_TITLES


class SeasonalWindowTests(unittest.TestCase):
    def target(self, handles):
        windows = object.__new__(WaylandWindows)
        windows.handles = handles
        return windows.target()

    def test_current_page_and_legacy_window_are_targetable(self):
        html = (Path(__file__).parents[1] / 'halloween_hub/static/index.html').read_text()
        title = re.search(r'<title>(.*?)</title>', html).group(1)
        self.assertTrue(title.startswith(WINDOW_TITLES))
        for name in (title, 'Halloween Hub'):
            with self.subTest(title=name):
                self.assertEqual(self.target({7: dict(title=name + ' - Chromium', app_id='chromium', states=[2])})[0], 7)

    def test_unrelated_windows_are_excluded_and_active_app_preferred(self):
        windows = {
            1: dict(title='Other site - Chromium', app_id='chromium', states=[2]),
            2: dict(title=WINDOW_TITLES[1], app_id='text-editor', states=[2]),
            3: dict(title='Halloween Hub - Chromium', app_id='chromium', states=[]),
            4: dict(title=WINDOW_TITLES[1], app_id='chromium', states=[2]),
        }
        self.assertEqual(self.target(windows)[0], 4)
        with self.assertRaises(OSError):
            self.target({key: windows[key] for key in (1, 2)})
