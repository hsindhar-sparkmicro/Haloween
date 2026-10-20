"""Copy selected local folders into a running Hub through its validated audio API."""
import argparse
import json
from pathlib import Path
import urllib.request
import uuid

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8080')
parser.add_argument('--music',type=Path)
parser.add_argument('--effects',type=Path)
parser.add_argument('--report',type=Path)
args=parser.parse_args()
results=[]
for kind,folder in [('tracks',args.music),('effects',args.effects)]:
    if folder is None:continue
    if not folder.is_dir():parser.error(f'Folder does not exist: {folder}')
    for path in sorted(folder.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in ('.mp3','.wav','.ogg'):continue
        if path.stat().st_size>100*1024*1024:raise ValueError(f'File exceeds 100 MB: {path.name}')
        boundary='Hub'+uuid.uuid4().hex
        # Fixed multipart filename does not interpolate user names into HTTP headers.
        safe=path.name.replace('"','_').replace('\r','_').replace('\n','_')
        header=f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{safe}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()
        data=header+path.read_bytes()+f'\r\n--{boundary}--\r\n'.encode()
        req=urllib.request.Request(args.url.rstrip('/')+'/api/'+kind,data,{'Content-Type':'multipart/form-data; boundary='+boundary},method='POST')
        with urllib.request.urlopen(req,timeout=60) as response:result=json.load(response)
        results.append(dict(library=kind,file=path.name,**result))
if args.report:
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(results,indent=2))
print(json.dumps({'files':len(results),'new':sum(not r['duplicate'] for r in results),'duplicates':sum(r['duplicate'] for r in results),'tracks':sum(r['library']=='tracks' for r in results),'effects':sum(r['library']=='effects' for r in results)}))
