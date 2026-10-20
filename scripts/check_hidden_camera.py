"""Pi scan/rest lifecycle; numerical state only, no captured images."""
import json,subprocess
from pathlib import Path
ssh=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=/dev/null','spark@192.168.0.100','python3 -']
script='''import json,time,urllib.request,subprocess
base='http://127.0.0.1:8092/api'
def request(path,data=None,method='GET'):
 r=urllib.request.Request(base+path,json.dumps(data).encode() if data is not None else None,{'Content-Type':'application/json'},method=method)
 return json.load(urllib.request.urlopen(r))
request('/settings',{'camera_cooldown':20,'camera_scan_seconds':8,'camera_threshold':30},'PATCH')
samples=[]
try:
 request('/camera',{'action':'arm'},'POST');start=time.monotonic();first_rest=None;second_scan=False
 while time.monotonic()-start<50:
  camera=request('/state')['camera'];samples.append(dict(seconds=round(time.monotonic()-start,2),**camera))
  assert 'has_frame' not in camera and 'frame' not in camera
  assert not camera['error'],camera
  if camera['scans']==1 and camera['status']=='Resting' and first_rest is None:
   first_rest=time.monotonic();processes=subprocess.run(['pgrep','-af','camera_worker.py'],capture_output=True,text=True).stdout
   assert not processes.strip(),processes
  if first_rest and camera['capture_active'] and camera['scans']>=2:
   assert time.monotonic()-first_rest>=19,('Rest too short',time.monotonic()-first_rest);second_scan=True
  if second_scan and camera['scans']>=2 and camera['status']=='Resting':break
  time.sleep(.5)
 assert first_rest and second_scan,(first_rest,second_scan,samples[-1])
 for action in ('preview','mirror'):
  try:request('/camera',{'action':action},'POST');raise AssertionError('Preview accepted')
  except urllib.error.HTTPError as e:assert e.code==400
 try:request('/camera/frame');raise AssertionError('Frame export accepted')
 except urllib.error.HTTPError as e:assert e.code==410
 print(json.dumps({'samples':samples,'two_scan_rest_cycles':True,'no_worker_during_rest':True,'frame_export_disabled':True,'physical_visitor_walkthrough':'Not qualified; deterministic motion samples verify trigger logic.'}))
finally:
 request('/camera',{'action':'stop'},'POST');request('/settings',{'camera_cooldown':45,'camera_threshold':4},'PATCH')
'''
result=subprocess.run(ssh,input=script,text=True,capture_output=True,check=True);data=json.loads(result.stdout);Path('validation/pi-hidden-camera.json').write_text(json.dumps(data,indent=2));print(json.dumps({'cycles':data['two_scan_rest_cycles'],'samples':len(data['samples']),'temperature':data['samples'][-1]['temperature'],'hidden':True}))
