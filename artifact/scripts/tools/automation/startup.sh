gi#!/bin/bash
cd var/www/html/drummer || exit
source venver/bin/activate
python3 app.py &