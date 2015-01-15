#!/bin/sh

curl "http://localhost:8983/solr/admin/collections?action=DELETE&name=citi"
curl "http://localhost:8983/solr/admin/collections?action=DELETE&name=citi_py"
#uncomment if you want to delete the full
#curl "http://localhost:8983/solr/admin/collections?action=DELETE&name=citi_full"