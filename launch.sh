#! /bin/sh
cd collection/
./csvToJsonConverter.py
./clustering.py ; R -f clusterize.R ; cd ..
python -m SimpleHTTPServer 8000
