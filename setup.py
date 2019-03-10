#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="flask-core",
    version="0.0.1",
    author="Carey Li, Sean Yeoh, Zain Afzal",
    author_email="cs6443@cse.unsw.edu.au",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["flask", "psycopg2", "psycopg2-binary", "SQLAlchemy", "cryptography"],
    package_data={"flask-core": ["templates/*/*"]},
)
