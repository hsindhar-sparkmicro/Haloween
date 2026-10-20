"""Compatibility entry point; current visual checks use the immersive player."""
import runpy
import sys
from pathlib import Path
sys.argv = [item for item in sys.argv if item != '--isolated']
runpy.run_path(str(Path(__file__).with_name('check_immersive.py')), run_name='__main__')
