#!/usr/bin/env python

from setuptools import find_namespace_packages, setup

setup(
    name="construction_finder",
    description="Construction Finder",
    author="Julia Kuiznetsova",
    author_email="juliakzn@gmail.com",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    package_data={"construction_finder": ["src/construction_finder/"]},
    include_package_data=True,
    version="0.0.0",
)
