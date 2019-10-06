#!/usr/bin/env python
"""
Setup for pytijo
"""
from setuptools import setup, find_packages

import os
import re

if os.environ.get("CI_COMMIT_TAG"):
    version = os.environ["CI_COMMIT_TAG"]
    if version.startswith("v"):
        version = version[1:]
        if not re.search(r"^\d+\.\d+\.\d+$", version):
            raise AttributeError(
                "given CI_COMMIT_TAG {} incorrect format. It must be vX.Y.Z or X.Y.Z format".format(
                    os.environ["CI_COMMIT_TAG"]
                )
            )
elif os.environ.get("CI_JOB_ID"):
    version = os.environ["CI_JOB_ID"]
else:
    version = None

setup(
    name="pytijo",
    version="0.0.1",
    description="Structure semi-structured text",
    license="Apache",
    author="Darin Sikanic",
    author_email="darin.sikanic@gmail.com",
    url="https://github.com/tijo-io/pytijo",
    packages=find_packages(exclude=["tests"]),
    install_requires=["six"],
    keywords="pytijo tijo structifytext structure text network cli parser",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
)
