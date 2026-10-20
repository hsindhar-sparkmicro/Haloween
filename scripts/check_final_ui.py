"""Modal error feedback, failed-edit rollback, countdown separation and effects."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
base='http://127.0.0.1:8080'
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={'width':800,'height':480})
    page.goto(base)
    page.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")')
    original=page.request.get(base+'/api/state').json()['settings']['party_date']
    record=None
    try:
        page.request.patch(base+'/api/settings',data={'party_date':'2030-10-20T20:00'})
        page.wait_for_function('() => document.querySelector("#party .countdown-target").textContent.includes("Oct 20, 2030")')
        assert 'Oct 31' in page.locator('#dashboard .countdown-target').inner_text()
        page.locator('[data-open="settings-dialog"]').last.click()
        page.locator('#setting-timezone').fill('Invalid/Zone')
        page.locator('#save-settings').click()
        page.wait_for_function('() => !document.querySelector("#toast").hidden && document.querySelector("#toast").closest("dialog")?.id==="settings-dialog"')
        assert page.locator('#settings-dialog').evaluate('(e) => e.open')
        page.screenshot(path='validation/settings-error-800x480.png')
        page.locator('#settings-dialog [data-close]').click()
        page.locator('[data-screen="party"]').click()
        page.locator('[data-open="music-dialog"]').click()
        page.locator('#music-upload').set_input_files({'name':'__qa_invalid.mp3','mimeType':'audio/mpeg','buffer':b'not an audio file'})
        page.wait_for_function('() => document.querySelector("#toast").textContent.includes("Unsupported audio") && document.querySelector("#toast").closest("dialog")?.id==="music-dialog"')
        visible=page.evaluate('''() => {const t=document.querySelector('#toast').getBoundingClientRect(),d=document.querySelector('#music-dialog').getBoundingClientRect();return t.top>=d.top&&t.bottom<=d.bottom;}''')
        assert visible
        page.screenshot(path='validation/audio-error-800x480.png')
        page.locator('#music-dialog [data-close]').click()
        record=page.request.post(base+'/api/records',data={'kind':'task','name':'__qa_failed_edit'}).json()['id']
        page.wait_for_timeout(1200)
        page.locator('[data-open="tasks-dialog"]').click()
        row=page.locator('#task-list .record-row').filter(has_text='__qa_failed_edit')
        row.wait_for()
        page.route('**/api/records/*',lambda route:route.abort())
        row.locator('input').check()
        page.wait_for_function('() => ![...document.querySelectorAll("#task-list .record-row")].find(e=>e.textContent.includes("__qa_failed_edit")).querySelector("input").checked')
        assert page.locator('#toast').evaluate('(e) => e.closest("dialog").id')=='tasks-dialog'
        page.unroute('**/api/records/*')
        page.locator('#tasks-dialog [data-close]').click()
        page.locator('#trick-mode').click()
        assert page.locator('#party').evaluate('(e) => e.classList.contains("trick-mode")')
        assert 'art-sheet.png' in page.locator('.party-particles span').first.evaluate('(e) => getComputedStyle(e).backgroundImage')
        page.screenshot(path='validation/party-ghosts-800x480.png')
        reports={'separate_halloween_and_party_countdowns':True,'modal_settings_error':True,'visible_audio_error':True,'failed_checkbox_rollback':True,'ghost_particles':True}
        Path('validation/final-ui-report.json').write_text(json.dumps(reports,indent=2))
        print(json.dumps(reports))
    finally:
        page.request.patch(base+'/api/settings',data={'party_date':original})
        if record:page.request.delete(base+'/api/records/'+str(record))
        browser.close()
