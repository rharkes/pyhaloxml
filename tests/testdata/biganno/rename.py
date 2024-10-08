"""Anonymize filenames."""

import uuid
from pathlib import Path

pth = Path(Path.cwd(), "tests", "testdata", "biganno")
files = [x for x in pth.glob("*.annotations")]
for file in files:
    newname = Path(file.parent, str(uuid.uuid4()).replace("-", "") + file.suffix)
    file.rename(newname)
