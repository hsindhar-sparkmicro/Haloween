import json
from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={'width':800,'height':480})
    page.goto('http://127.0.0.1:8080')
    page.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")')
    assert page.evaluate('() => ["music","ambience","effect"].every(id=>document.querySelector("#"+id+"-player").paused)')
    page.route('**/api/state',lambda route:route.abort())
    page.wait_for_function('() => document.querySelector("#connection").textContent.includes("Reconnecting")')
    page.unroute('**/api/state')
    page.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")')
    page.locator('[data-open="settings-dialog"]').last.click()
    page.locator('#location-query').fill('Toronto');page.locator('#search-location').click()
    page.locator('#location-results button').first.wait_for(timeout=20000)
    page.locator('#location-results button').first.click()
    page.locator('#setting-reduced_motion').check();page.locator('#save-settings').click()
    page.wait_for_function('() => document.body.classList.contains("reduced-motion")')
    for _ in range(30):
        response=page.request.get('http://127.0.0.1:8080/api/state').json()
        if response['weather']['status']=='fresh':break
        page.wait_for_timeout(1000)
    assert response['weather']['status']=='fresh',response['weather']
    page.screenshot(path='validation/weather-800x480.png')
    Path('validation/resilience-report.json').write_text(json.dumps({'start_muted':True,'reconnect':True,'reduced_motion':True,'location':response['settings']['location'],'weather':response['weather']},indent=2))
    page.request.patch('http://127.0.0.1:8080/api/settings',data={'reduced_motion':False})
    browser.close()
    print('Start-muted, reconnect, reduced motion, location search, and live weather passed.')
