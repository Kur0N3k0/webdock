#!/bin/sh

rm -rf ./upload/*
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf