#!/bin/sh

echo "Indexing Sample data"
python src/python/setup.py -i data/2013-07-citi-sample.csv -l citi_py
python src/python/setup.py -i data/2013-08-citi-sample.csv -l citi_py
python src/python/setup.py -i data/2013-09-citi-sample.csv -l citi_py
python src/python/setup.py -i data/2013-10-citi-sample.csv -l citi_py

# To index full:
# python ./src/python/setup.py -i data/full/citi-bike/ -l citi_full