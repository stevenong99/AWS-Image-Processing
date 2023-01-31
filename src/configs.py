from pathlib import Path
from torch import hub


# Initializing all the important folder paths
ROOT = Path(__file__).parent
RESOURCES = ROOT / ("res")

# Setting pytorch to use a folder inside the project to download 
# the models to, for easy deployment into offline environments
hub.set_dir(str(RESOURCES))
