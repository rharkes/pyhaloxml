from distutils.core import setup, Extension
from pathlib import Path


def main():
    setup(ext_modules=[Extension("pointinpoly", sources=["src/pointinpoly.c"])])


if __name__ == "__main__":
    main()
