import tempfile
import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from halloween_hub.sneak_peek import sneak_peek_calendar
from halloween_hub.app import create_app


class SneakPeekCalendarTests(unittest.TestCase):
    def test_november_calendar(self):
        result = sneak_peek_calendar('America/Toronto', datetime(2026, 11, 3, 12, tzinfo=ZoneInfo('America/Toronto')))
        self.assertTrue(result['black_friday']['target'].startswith('2026-11-27'))
        self.assertEqual(result['black_friday']['days'], 24)
        self.assertEqual(result['christmas']['days'], 52)
        self.assertTrue(result['boxing_day']['target'].startswith('2026-12-26'))
        self.assertEqual(result['defrost_percent'], 6)

    def test_local_christmas_day_and_passed_dates(self):
        instant = datetime(2026, 12, 25, 2, tzinfo=timezone.utc)
        self.assertEqual(sneak_peek_calendar('America/Toronto', instant)['christmas']['phase'], 'upcoming')
        self.assertEqual(sneak_peek_calendar('Europe/Paris', instant)['christmas']['phase'], 'today')
        result = sneak_peek_calendar('America/Toronto', datetime(2026, 12, 26, 18, tzinfo=timezone.utc))
        self.assertEqual(result['christmas']['phase'], 'past')
        self.assertEqual(result['christmas']['seconds'], 0)
        self.assertEqual(result['boxing_day']['phase'], 'today')

    def test_dst_seconds_and_year_rollover(self):
        now = datetime(2026, 10, 31, 12, tzinfo=ZoneInfo('America/Toronto'))
        result = sneak_peek_calendar('America/Toronto', now)
        expected = datetime(2026, 12, 25, tzinfo=ZoneInfo('America/Toronto')).timestamp() - now.timestamp()
        self.assertEqual(result['christmas']['seconds'], expected)
        next_year = sneak_peek_calendar('America/Toronto', datetime(2027, 1, 2, tzinfo=timezone.utc))
        self.assertTrue(next_year['christmas']['target'].startswith('2027-12-25'))
        self.assertTrue(next_year['black_friday']['target'].startswith('2027-11-26'))
        self.assertEqual(next_year['defrost_percent'], 0)

    def test_party_settings_and_halloween_countdown_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            app = create_app(root)
            try:
                client = app.test_client()
                client.patch('/api/settings', json={'party_date': '2030-10-20T20:00', 'timezone':'America/Toronto'})
                state = client.get('/api/state').json
                self.assertIn('sneak_peek', state)
                self.assertTrue(state['party_countdown']['target'].startswith('2030-10-20'))
                self.assertIn('-10-31', state['countdown']['target'])
                self.assertEqual(state['settings']['party_date'], '2030-10-20T20:00')
            finally:
                app.extensions['camera'].close()
                app.extensions['simulation'].close()


if __name__ == '__main__':
    unittest.main()
