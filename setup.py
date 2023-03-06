import setuptools
from Cython.Build import cythonize
from pathlib import Path

setuptools.setup(
    name="c_inpoly",
    ext_modules=cythonize(
        [str(Path("src", "pyhaloxml", "cython", "c_inpoly.pyx"))],
        compiler_directives={"language_level": "3"},
    ),
    ext_package="pyhaloxml.cython",
)
