import os
import runpy
from setuptools import setup, find_packages

# Get version
cwd = os.path.abspath(os.path.dirname(__file__))
versionpath = os.path.join(cwd, 'synthpops', 'version.py')
version = runpy.run_path(versionpath)['__version__']

CLASSIFIERS = [
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GPLv3",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Development Status :: 1",
    "Programming Language :: Python :: 3.7",
]

setup(
    name="synthpops",
    version=version,
    author="Dina Mistry, Cliff Kerr",
    author_email="dmistry@idmod.org",
    description="Synthetic population generation",
    keywords=['synthetic population', 'census', 'demography'],
    platforms=["OS Independent"],
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "sciris>=0.16.1",
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "numba",
        "networkx",
    ],
)
