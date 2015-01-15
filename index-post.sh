#!/bin/sh

cd solr-5.0.0-SNAPSHOT
echo "Indexing Sample data"
bin/post -c citi ../data/2013-07-citi-sample.csv
bin/post -c citi ../data/2013-08-citi-sample.csv
bin/post -c citi ../data/2013-09-citi-sample.csv
bin/post -c citi ../data/2013-10-citi-sample.csv
