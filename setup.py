from pathlib import Path
from setuptools import setup


def get_version(pkg_name):
    version_filename = Path(Path(__file__).parent, pkg_name, "version.py")
    with open(version_filename) as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                sep = '"' if '"' in line else "'"
                return line.split(sep)[1]
    raise RuntimeError(f"Version not found in {version_filename}")


PACKAGE_NAME = "haloxml"
setup(
    name=PACKAGE_NAME,
    version=get_version(PACKAGE_NAME),
    description="A reader for the .annotations files from halo.",
    packages=[PACKAGE_NAME],
)
