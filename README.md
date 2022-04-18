# pyced

A python wrapper package for the CEBAF element database (CED) web API.

## Overview 
A light wrapper that handles common queries to the CED.  Only a small portion of the CED web API has been
wrapped so far, including the Inventory call and hierarchical type checking.  Some of this was based on the existing
ced2gnn software.

## Installation
This code has not been packaged up for release through PyPI, etc. but is installable directly from GitHub.  This is
developed against the standard pubtools Python 3.7 installation.

To install the latest version from source:

```bash
pip install git+https://github.com/JeffersonLab/pyced.git
```

To install a specific tag (typically a version):

```bash
pip install git+https://github.com/JeffersonLab/pyced.git@v0.1.0
```

## Running tests
```bash
git clone https://github.com/JeffersonLab/pyced.git
cd pyced
python3.7 setup.py test
```
