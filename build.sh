#!/usr/bin/env bash
# exit on error
set -o errexit

# upgrade pip and install packages
pip install --upgrade pip
pip install -r requirements.txt