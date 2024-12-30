#!/bin/bash

# Upload project to pypi

rm -rf ./dist
rm -rf ./src/dataxi.egg-info

python setup_helper.py

python -m build

python -m twine upload dist/*
