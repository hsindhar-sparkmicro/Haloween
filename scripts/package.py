"""Portable source package, manifest generated from its exact inventory."""
import hashlib
import zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
version_ns={}
exec((root/'halloween_hub'/'version.py').read_text(),version_ns)
version=version_ns['VERSION']
out=root/'dist';out.mkdir(exist_ok=True)
package=out/f'HalloweenHub-{version}-source.zip'
files=[]
for directory in ['halloween_hub','scripts','tests']:
    files.extend(p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend(root/name for name in ['requirements.txt','requirements-dev.txt','run.sh','run.ps1','kiosk.sh','README.md','ARTWORK.md','VALIDATION.md','API.md','SNEAK-PEEK.md','UPDATES.md','design-sneak-fusion-prompt.txt','sneak-peek-artwork.json'])
# Include test evidence so documentation image links resolve after extraction.
files.extend(p for p in (root/'validation').rglob('*') if p.is_file() and p.suffix in ('.json','.jsonl','.png','.txt'))
files.extend(p for p in (out/'pi-wheels').glob('*.whl'))
manifest=[]
with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(set(files)):
        name=path.relative_to(root).as_posix()
        if name.startswith('dist/pi-wheels/'):name=name[5:]
        archive.write(path,'HalloweenHub/'+name)
        manifest.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+name)
    archive.writestr('HalloweenHub/SHA256SUMS','\n'.join(manifest)+'\n')
checksum=hashlib.sha256()
with package.open('rb') as source:
    for block in iter(lambda:source.read(1024*1024),b''):
        checksum.update(block)
digest=checksum.hexdigest()
package.with_suffix('.zip.sha256').write_text(digest+'  '+package.name+'\n')
print(package)
