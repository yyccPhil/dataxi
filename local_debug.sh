#!/bin/bash

# rebuild the local installation package

rm -rf ./dist
rm -rf ./dataxi.egg-info

python setup_helper.py

python -m build

pip uninstall dataxi

# read the version number from the VERSION file
version=$(cat VERSION)

pip install ./dist/dataxi-${version}.tar.gz
