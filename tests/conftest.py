import sys
from pathlib import Path

p = Path(__file__)
if p.parent.parent.parent.resolve().as_posix() not in sys.path:
    sys.path.insert(0, p.parent.parent.resolve().as_posix())

print(sys.path)
