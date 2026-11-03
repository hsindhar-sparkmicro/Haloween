"""Calendar facts for the isolated November sneak-peek edition."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def sneak_peek_calendar(timezone, now=None):
    zone = ZoneInfo(timezone)
    now = (now or datetime.now(zone)).astimezone(zone)
    year = now.year
    november = datetime(year, 11, 1, tzinfo=zone)
    thanksgiving = november + timedelta(days=(3 - november.weekday()) % 7 + 21)
    dates = {
        'christmas': datetime(year, 12, 25, tzinfo=zone),
        'black_friday': thanksgiving + timedelta(days=1),
        'boxing_day': datetime(year, 12, 26, tzinfo=zone),
    }
    result = {}
    for key, target in dates.items():
        phase = 'today' if now.date() == target.date() else 'past' if now.date() > target.date() else 'upcoming'
        result[key] = dict(target=target.isoformat(), seconds=max(0, int(target.timestamp() - now.timestamp())),
                           days=max(0, (target.date() - now.date()).days), phase=phase)
    # A calendar joke from Nov 1 to Dec 1, never an actual artist status.
    result['defrost_percent'] = max(0, min(100, int((now.date() - november.date()).days / 30 * 100)))
    result['timezone'] = timezone
    # A fixed Montréal event, independent of the configurable personal party date.
    party = datetime(2026, 12, 9, 17, tzinfo=ZoneInfo('America/Toronto'))
    party_now = now.astimezone(party.tzinfo)
    result['spark_party'] = dict(
        target=party.isoformat(), timezone='America/Toronto',
        seconds=max(0, int(party.timestamp() - now.timestamp())),
        phase='upcoming' if now < party else 'today' if party_now.date() == party.date() else 'past',
    )
    return result
