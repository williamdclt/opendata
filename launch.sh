#! /bin/sh
cd collection/
./csvToJsonConverter.py
cd ..
python -m SimpleHTTPServer 8000
