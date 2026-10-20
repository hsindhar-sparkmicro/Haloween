"""Exit successfully when the exact runtime requirements are already installed."""
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
import sys
for line in (Path(__file__).resolve().parents[1] / 'requirements.txt').read_text().splitlines():
    if not line or line.startswith('#'): continue
    name, required = line.split('==')
    try:
        if version(name) != required: sys.exit(1)
    except PackageNotFoundError:
        sys.exit(1)
