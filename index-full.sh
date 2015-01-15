#!/bin/sh

echo "Indexing Sample data"

# To index full:
date
python ./src/python/setup.py -i data/full/ -l citi_full
date