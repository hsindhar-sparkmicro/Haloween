"""Guard cached dashboard rendering against stale weather, units and timezones."""
import json
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

url='http://127.0.0.1:8092'
state=json.load(urlopen(url+'/api/state'))
state['settings'].update(timezone='America/Toronto',units='C',location={'name':'Montréal'})
state['weather'].update(status='fresh',current={'temperature_2m':10,'apparent_temperature':8,'wind_speed_10m':5,'weather_code':3})
state['sneak_peek']['christmas']['target']='2026-12-25T02:00:00+00:00'
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={'width':800,'height':480})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('**/api/state',lambda route:route.fulfill(json=state))
    page.goto(url)
    page.wait_for_function('()=>document.querySelector("#temperature").textContent==="10.0°C"')
    assert 'Dec 24' in page.locator('#dashboard .countdown-target').inner_text()
    page.evaluate("""()=>{window.weatherMutations=0;new MutationObserver(r=>weatherMutations+=r.length).observe(document.querySelector('.welcome-weather'),{subtree:true,childList:true,characterData:true,attributes:true});}""")
    before=page.locator('#peek-party-countdown').inner_text()
    page.wait_for_timeout(3100)
    assert page.evaluate('weatherMutations')==0
    assert page.locator('#peek-party-countdown').inner_text()!=before
    state['settings'].update(units='F',timezone='Asia/Tokyo',location={'name':'Tokyo'})
    state['weather']['current'].update(temperature_2m=20,weather_code=0)
    state['sneak_peek']['defrost_percent']=100
    page.wait_for_function('()=>document.querySelector("#temperature").textContent==="68.0°F"')
    assert page.locator('#weather-location').inner_text()=='Tokyo'
    assert page.locator('#weather-condition').inner_text()=='Clear skies'
    assert 'Dec 25' in page.locator('#dashboard .countdown-target').inner_text()
    assert 'Tokyo' in page.locator('#dashboard .countdown-target').inner_text()
    assert page.locator('.peek-defrost h2').inner_text()=='Mariah has defrosted.'
    assert not errors,errors
    report={'stableWeatherNoMutations':'pass','partyCountdownTicks':'pass','changedForecastLocationUnits':'pass','timezoneDateBoundary':'pass','defrostChange':'pass','pageErrors':errors}
    output=Path('validation/roaming-smooth/dashboard-refresh.json');output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    browser.close()
