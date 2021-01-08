#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import setuptools
from distutils.core import Command

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

if sys.version_info >= (3,8):
    sys.exit("Python version greater than 3.7 not supported because of numpy and moviepy compatibility issues with python version 3.8")

# This will store the models
network_folder_path = os.path.join(os.path.expanduser("~"), ".katna")
if not os.path.exists(network_folder_path):
    os.mkdir(network_folder_path)

# helper functions to make it easier to list dependencies not as a python list, but vertically w/ optional built-in comments to why a certain version of the dependency is listed
def cleanup(x):
    return re.sub(r" *#.*", "", x.strip())  # comments


def to_list(buffer):
    return list(filter(None, map(cleanup, buffer.splitlines())))


# normal dependencies ###
#
# these get resolved and installed via either of these two:
#
#   pip install katna
#   pip install -e .
#
# IMPORTANT: when updating these, please make sure to sync conda/meta.yaml
dep_groups = {
    "core": to_list(
        """
        scipy
        scikit-learn
        scikit-image
        opencv-contrib-python>=3.4.7
        numpy>=1.15
        imutils
        requests
        moviepy >=1.0.1, <=1.0.3
"""
    )
}

__version__ = None # Explicitly set version.
exec(open('Katna/version.py').read()) # loads __version__

requirements = [y for x in dep_groups.values() for y in x]
setup_requirements = to_list(
    """
    pytest-runner
    setuptools>=36.2
"""
)


# test dependencies ###
test_requirements = to_list(
    """
    pytest
"""
)


setuptools.setup(
    name="katna",
    version=__version__,
    author="keplerlab",
    author_email="keplerwaasi@gmail.com",
    description="Katna is a tool that automates video key/best frames extraction.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/keplerlab/Katna.git",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "https://katna.readthedocs.io",
        "Source": "https://github.com/keplerlab/Katna",
        "Tracker": "https://github.com/keplerlab/Katna/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
