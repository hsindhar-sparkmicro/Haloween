"""Copy browser-compatible cutscene files into app data; preserve source files."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from halloween_hub.core import data_directory

parser=argparse.ArgumentParser();parser.add_argument('file',type=Path);parser.add_argument('--webm',type=Path);parser.add_argument('--name',default='welcome');parser.add_argument('--data-dir',type=Path);args=parser.parse_args()
if not re.fullmatch(r'[a-z0-9_-]+',args.name):parser.error('Name must use lowercase letters, numbers, underscores or hyphens')
sources=[(args.file,args.name+'.mp4')]+([(args.webm,args.name+'.webm')] if args.webm else [])
for source,name in sources:
 if not source.is_file() or source.suffix.lower()!=Path(name).suffix or not 16<=source.stat().st_size<=250*1024*1024:parser.error('Choose valid MP4/WebM files smaller than 250 MB')
 with source.open('rb') as stream:header=stream.read(12)
 if name.endswith('.mp4') and header[4:8]!=b'ftyp':parser.error('Invalid MP4 header')
 if name.endswith('.webm') and header[:4]!=b'\x1aE\xdf\xa3':parser.error('Invalid WebM header')
directory=(args.data_dir or data_directory())/'cutscenes';directory.mkdir(parents=True,exist_ok=True)
prepared=[];results=[]
try:
 for source,name in sources:
  with tempfile.NamedTemporaryFile(dir=directory,delete=False) as stream:
   temporary=Path(stream.name);prepared.append((temporary,directory/name))
   with source.open('rb') as incoming:shutil.copyfileobj(incoming,stream)
 for temporary,destination in prepared:
  temporary.replace(destination)
  results.append({'file':str(destination),'bytes':destination.stat().st_size,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()})
finally:
 for temporary,_ in prepared:temporary.unlink(missing_ok=True)
print(json.dumps({'files':results}))
