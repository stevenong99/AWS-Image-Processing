from pathlib import Path
from torch import hub

ROOT = Path(__file__).parent
RESOURCES = ROOT / ("res")

hub.set_dir(str(RESOURCES))
