#!/bin/bash

export PYTHONPATH=/app/src/node_modules/.local/lib/python2.7/site-packages
export PATH=$PATH:/app/src/node_modules/node_modules/.local/bin

python server.py
