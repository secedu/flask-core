#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="flask-core",
    version="2.7.0",
    author="Carey Li, Sean Yeoh, Zain Afzal",
    author_email="cs6443@cse.unsw.edu.au",
    description="A modular Flask core for CTF war-games, originally created for CS6443",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/secedu/flask-core",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["flask", "psycopg2", "psycopg2-binary", "SQLAlchemy", "cryptography"],
    package_data={"flask-core": ["templates/*/*"]},
    classifiers=["Programming Language :: Python :: 3"],
)
