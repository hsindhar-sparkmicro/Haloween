"""Discover only installed gallery media in app data."""
import re

def cutscenes(root):
    directory=root/'cutscenes'
    paths=sorted(directory.glob('*.mp4'),key=lambda p:(p.stem!='welcome',p.name))
    return [dict(id=p.stem,name=p.stem.replace('-',' ').title(),url='/api/cutscenes/'+p.name,
                 webm_url='/api/cutscenes/'+p.with_suffix('.webm').name if p.with_suffix('.webm').is_file() else None)
            for p in paths if re.fullmatch(r'[a-z0-9_-]+',p.stem)]

def backgrounds(root):
    return [dict(id=p.stem,url='/api/backgrounds/'+p.name) for p in sorted((root/'backgrounds').glob('*.png'))]
