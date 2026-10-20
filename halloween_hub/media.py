"""Validated, content-addressed local audio imports; repeated imports are idempotent."""
import hashlib
from pathlib import Path
import tempfile
import threading
from werkzeug.utils import secure_filename

_import_lock=threading.Lock()

def import_audio(store,file,kind='tracks'):
    if kind not in ('tracks','effects'):raise ValueError('Unknown audio library')
    if not file or not file.filename:raise ValueError('Choose an audio file')
    name=secure_filename(file.filename)
    extension=Path(name).suffix.lower().lstrip('.')
    signature=file.stream.read(64);file.stream.seek(0)
    valid=((extension=='wav' and signature[:4]==b'RIFF' and signature[8:12]==b'WAVE') or
           (extension=='ogg' and signature[:4]==b'OggS') or
           (extension=='mp3' and (signature[:3]==b'ID3' or (len(signature)>1 and signature[0]==255 and signature[1]&224==224))))
    if not valid:raise ValueError('Unsupported audio: choose a valid MP3, WAV, or OGG file')
    directory=store.root/('music' if kind=='tracks' else 'effects');directory.mkdir(exist_ok=True)
    temporary=None;destination=None
    try:
        digest=hashlib.sha256();size=0
        with tempfile.NamedTemporaryFile(dir=directory,delete=False) as output:
            temporary=Path(output.name)
            while chunk:=file.stream.read(1024*1024):
                size+=len(chunk)
                if size>100*1024*1024:raise ValueError('Choose a file smaller than 100 MB')
                output.write(chunk);digest.update(chunk)
        filename=digest.hexdigest()+'.'+extension
        with _import_lock,store.connect() as db:
            existing=db.execute(f'SELECT id,name FROM {kind} WHERE filename=?',(filename,)).fetchone()
            if existing:return dict(id=existing[0],name=existing[1],duplicate=True)
            destination=directory/filename
            temporary.replace(destination)
            cursor=db.execute(f'INSERT INTO {kind}(name,filename) VALUES(?,?)',(name,filename))
        return dict(id=cursor.lastrowid,name=name,duplicate=False)
    except Exception:
        if destination:destination.unlink(missing_ok=True)
        raise
    finally:
        if temporary:temporary.unlink(missing_ok=True)
