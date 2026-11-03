"""Exercise release status/settings against the running app; fixtures cover future releases."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('validation/sneak-peek/updates');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch();page=b.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    for w,h in [(800,480),(1280,720),(390,844)]:
        page.set_viewport_size({'width':w,'height':h});page.goto('http://127.0.0.1:8092/')
        page.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
        page.keyboard.press('Escape');page.locator('nav [data-open="settings-dialog"]').click()
        page.locator('#release-check').scroll_into_view_if_needed()
        assert page.locator('#release-version').inner_text().startswith('Version 1.1.0-sneak.1')
        assert page.locator('#release-status').inner_text()
        assert page.locator('#release-package').is_hidden()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(out/f'settings-{w}.png'))
        page.locator('#release-check').click()
        page.wait_for_function('()=>!document.querySelector("#release-check").disabled')
        page.keyboard.press('Escape')
    page.keyboard.press('Escape');page.locator('nav [data-open="settings-dialog"]').click()
    box=page.locator('#setting-auto_download_updates')
    original=box.is_checked()
    try:
        box.set_checked(not original);page.locator('#save-settings').click()
        page.wait_for_function('(v)=>fetch("/api/state").then(r=>r.json()).then(s=>s.settings.auto_download_updates===v)',arg=not original)
        page.keyboard.press('Escape');page.locator('nav [data-open="settings-dialog"]').click()
        assert box.is_checked()!=original
        page.keyboard.press('Escape')
    finally:
        page.request.patch('http://127.0.0.1:8092/api/settings',data={'auto_download_updates':original})
    # Do not publish a release merely to test the ready-state presentation.
    def fixture(route):
        data=route.fetch().json()
        data['updates'].update(status='ready',message='Version 1.2.0 downloaded and verified. Ready for installation.',download_url='/api/updates/package',filename='HalloweenHub-1.2.0-source.zip',busy=False)
        route.fulfill(json=data)
    page.route('**/api/state',fixture)
    page.reload();page.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
    page.keyboard.press('Escape');page.locator('nav [data-open="settings-dialog"]').click()
    page.locator('#release-package').scroll_into_view_if_needed()
    assert page.locator('#release-package').is_visible()
    assert page.locator('#release-package').get_attribute('href')=='/api/updates/package'
    page.screenshot(path=str(out/'ready-fixture.png'))
    assert not errors,errors
    report={'liveSettings':'pass','autoDownloadPreference':'pass','readyLinkFixture':'pass','views':[800,1280,390],'pageErrors':errors}
    (out/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));b.close()
