#!/bin/bash
python3 tree_maker.py
git add .
git commit -m "Update"
git push -F
