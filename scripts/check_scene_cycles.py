"""Full eight-scene Pi cycles; use a dedicated test backend to avoid live selections."""
import runpy
import sys
from pathlib import Path
if len(sys.argv)==1:
    sys.argv += ['--cdp','http://127.0.0.1:19223','--url','http://127.0.0.1:8090','--cycles','--output','validation/pi-immersive-scenes']
runpy.run_path(str(Path(__file__).with_name('check_immersive.py')), run_name='__main__')
