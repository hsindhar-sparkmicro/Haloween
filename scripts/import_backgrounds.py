"""Copy local PNG backgrounds into application data, deduplicated by content."""
import argparse,hashlib,json,sys,tempfile,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from halloween_hub.core import data_directory
p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--data-dir',type=Path);args=p.parse_args()
root=(args.data_dir or data_directory())/'backgrounds';root.mkdir(parents=True,exist_ok=True);results=[]
for source in sorted(args.folder.glob('*.png')):
 with source.open('rb') as f:header=f.read(33)
 if len(header)<33 or header[:8]!=b'\x89PNG\r\n\x1a\n' or header[12:16]!=b'IHDR':raise ValueError('Invalid PNG: '+source.name)
 width,height=int.from_bytes(header[16:20],'big'),int.from_bytes(header[20:24],'big')
 if not (0<width<=8192 and 0<height<=8192):raise ValueError('PNG dimensions must be 1-8192 pixels')
 if source.stat().st_size>30*1024*1024:raise ValueError('Background exceeds 30 MB')
 digest=hashlib.sha256(source.read_bytes()).hexdigest();destination=root/(digest+'.png')
 if not destination.exists():
  temporary=None
  try:
   with tempfile.NamedTemporaryFile(dir=root,delete=False) as f:
    temporary=Path(f.name)
    with source.open('rb') as src:shutil.copyfileobj(src,f)
   temporary.replace(destination)
  finally:
   if temporary:temporary.unlink(missing_ok=True)
 results.append({'file':source.name,'sha256':digest})
print(json.dumps(results))
