import json
import threading
import time
from urllib.parse import urlencode
from urllib.request import urlopen


def fetch(url):
    with urlopen(url, timeout=6) as response:
        return json.load(response)


class Weather:
    def __init__(self, store):
        self.store = store
        self.lock = threading.Lock()
        self.refreshing = False
        self.retry_at = 0

    def snapshot(self, location):
        if not location:
            return dict(status='unset')
        key = f"{location['latitude']},{location['longitude']}"
        cached = self.store.get('weather', {})
        valid = cached.get('key') == key
        age = time.time() - cached.get('fetched', 0)
        with self.lock:
            if (not valid or age >= 900) and not self.refreshing and time.time() >= self.retry_at:
                self.refreshing = True
                threading.Thread(target=self.refresh, args=(dict(location), key), daemon=True).start()
        if valid:
            return dict(cached, status='fresh' if age < 900 else 'stale')
        return dict(status='loading' if self.refreshing else 'offline')

    def refresh(self, location, key):
        try:
            query = urlencode(dict(latitude=location['latitude'], longitude=location['longitude'],
                                   current='temperature_2m,apparent_temperature,weather_code,wind_speed_10m',
                                   hourly='temperature_2m', forecast_days=1, timezone='auto'))
            data = fetch('https://api.open-meteo.com/v1/forecast?' + query)
            self.store.put('weather', dict(key=key, fetched=time.time(), current=data['current'],
                                           hourly=data.get('hourly', {})))
            self.retry_at = 0
        except Exception:
            self.retry_at = time.time() + 60
        finally:
            with self.lock:
                self.refreshing = False


def search_locations(query):
    data = fetch('https://geocoding-api.open-meteo.com/v1/search?' + urlencode(dict(name=query, count=5, language='en', format='json')))
    return [dict(name=', '.join(filter(None, [r['name'], r.get('admin1'), r.get('country')])),
                 latitude=r['latitude'], longitude=r['longitude']) for r in data.get('results', [])]
