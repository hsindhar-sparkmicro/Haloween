"""Discover only installed gallery media in app data."""
import re

def cutscenes(root):
    directory=root/'cutscenes'
    paths=sorted(directory.glob('*.mp4'),key=lambda p:(p.stem!='welcome',p.name))
    return [dict(id=p.stem,name=p.stem.replace('-',' ').title(),url='/api/cutscenes/'+p.name,
                 webm_url='/api/cutscenes/'+p.with_suffix('.webm').name if p.with_suffix('.webm').is_file() else None)
            for p in paths if re.fullmatch(r'[a-z0-9_-]+',p.stem)]

# Stable content IDs retain the relationship when PNG imports use hash filenames.
BACKGROUND_VIDEOS = {
    '009045cb02d9164961af0df50811db59f4e951a7322cbb9d390f6979c088badb': 'nun',
    '0438919254cd3b10cf52f4a7be6ebffc24ac4f0fa56d2ce723625c039895791e': 'dracula',
    'wicked_nun': 'nun', 'nun': 'nun', 'dracula_stand': 'dracula', 'dracula': 'dracula',
}


def backgrounds(root):
    return [dict(id=p.stem,url='/api/backgrounds/'+p.name,video_id=BACKGROUND_VIDEOS.get(p.stem)) for p in sorted((root/'backgrounds').glob('*.png'))]
