"""Exercise scene playback and real kiosk minimize/restore on the test Pi."""
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ssh=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=/dev/null','spark@192.168.0.100']
def native(action=None):
    expression="manage()" if action is None else "manage('"+action+"')"
    command='cd ~/HalloweenHub-20261014; .venv/bin/python -c "import json; from halloween_hub.window import manage; print(json.dumps('+expression+'))"'
    return json.loads(subprocess.check_output(ssh+[command],text=True))
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp('http://127.0.0.1:19223',timeout=15000)
    page=[q for q in browser.contexts[0].pages if ':8088' in q.url][0]
    page.goto('http://127.0.0.1:8088/?kiosk=1')
    page.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")')
    page.locator('[data-screen="haunt"]').click()
    page.locator('#haunt-scene').select_option('Purple mist')
    page.wait_for_function('() => document.querySelector("#haunt-stage").textContent.includes("Purple mist") && document.querySelector("#activate-haunt").disabled')
    page.wait_for_function('() => !document.querySelector("#effect-player").paused')
    selected=page.evaluate('() => ({stage:document.querySelector("#haunt-stage").textContent,audio:document.querySelector("#effect-player").src})')
    page.locator('#scene-back').click()
    page.wait_for_function('()=>!document.querySelector("#activate-haunt").disabled')
    page.locator('#haunt-scene').select_option('Pumpkin parade')
    page.wait_for_function('() => document.querySelector("#haunt-stage").textContent.includes("Pumpkin parade")')
    page.locator('#scene-back').click()
    page.wait_for_function('()=>!document.querySelector("#activate-haunt").disabled')
    page.locator('#random-scene').click()
    page.wait_for_function('() => document.querySelector("#haunt-scene").value!=="Pumpkin parade"')
    random_scene=page.locator('#haunt-scene').input_value()
    page.screenshot(path='validation/pi-scene-playing.png')
    page.locator('#scene-back').click()
    page.wait_for_function('() => !document.querySelector("#activate-haunt").disabled')
    page.wait_for_function('() => !document.querySelector("#minimize-window").disabled')
    before=native()
    page.locator('#minimize-window').click()
    page.wait_for_timeout(600)
    minimized=native()
    subprocess.check_call(ssh+['XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0 grim ~/HalloweenHub-20261014/minimized.png'])
    subprocess.check_call(['scp','-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=/dev/null','spark@192.168.0.100:HalloweenHub-20261014/minimized.png','validation/pi-minimized.png'])
    assert 1 in minimized['window']['states'],minimized
    restored=native('restore')
    page.wait_for_timeout(500)
    page.locator('[data-screen="dashboard"]').click()
    if page.locator('#sound-toggle').get_attribute('aria-label')=='Mute audio':page.locator('#sound-toggle').click()
    page.screenshot(path='validation/pi-final-kiosk.png')
    report={'selected_scene':selected,'replacement_scene':True,'random_scene':random_scene,'window_before':before,'window_minimized':minimized,'window_restored':restored}
    Path('validation/pi-controls-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
