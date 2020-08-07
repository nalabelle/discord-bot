import sys
import logging
from pathlib import Path
packages = str(Path('data/extensions/site-packages').resolve())
if packages not in sys.path:
    sys.path.append(packages)

logging.getLogger().warn("\n".join(sys.path))

def setup(bot):
    pass

def teardown(bot):
    pass
