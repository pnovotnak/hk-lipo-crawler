# Preface

This is not my best work. It's not fast, it's not clean, but it *does work.*
If you'd like to put in some effort cleaning it up, extending it to other
parts or sites, drop me a line.

# Setup

`cd` to your clone of this repository

Get a virtualenv set up

    virtualenv env

Activate it

    source env/bin/activate

Then install requirements

    pip install -r requirements.txt

If you'd like to run the app more than once, do yourself and run

    pip install grequests==0.2.0

This will allow the crawler to make multiple requests at once, which reduces
the time it takes to crawl the HK site by a significant margin.

# Usage

Run `crawler.py` to get a json string of batteries.

Run `sorter.py` with the JSON of batteries to get a sorted CSV.

    python ./crawler.py > batteries.json
    python ./sorter.py < batteries.json

