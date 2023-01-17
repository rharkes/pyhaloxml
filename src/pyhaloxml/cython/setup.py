import setuptools
import Cython.Build

setuptools.setup(
    name="c_inpoly",
    ext_modules=Cython.Build.cythonize(
        "c_inpoly.pyx", compiler_directives={"language_level": "3"}
    ),
)
