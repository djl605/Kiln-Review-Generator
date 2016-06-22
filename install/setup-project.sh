#!/bin/bash

if [ ! -d node_modules ]; then
  mkdir node_modules
fi

if [ ! -f node_modules/get-pip.py ]; then
  curl https://bootstrap.pypa.io/get-pip.py -o node_modules/get-pip.py
fi

export HOME=/app/src/node_modules
export PATH=$PATH:/app/src/node_modules/.local/bin

python node_modules/get-pip.py --user
pip install --user -r install/requirements.txt
