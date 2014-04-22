# Preface

This is not my best work. It's not fast, it's not clean, but it *does work.* If you'd like to put in some effort cleaning it up, extending it to other parts or sites, drop me a line.

# Setup

`cd` to your clone of this repository

Get a virtualenv set up

    virtualenv env

Activate it

    source env/bin/activate

Then install requirements

    pip install -r requirements.txt


# Usage

Run `crawler.py` to get a json string of batteries.

Run `sorter.py` with the JSON of batteries to get a sorted CSV.

    python ./crawler.py > batteries.json
    python ./sorter.py < batteries.json

