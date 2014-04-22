# Setup

`cd` to your clone of this repository

Get a virtualenv set up

    virtualenv env

Then install requirements

    pip install -r requirements.txt


# Usage

Run `crawler.py` to get a json string of batteries.

Run `sorter.py` with the JSON of batteries to get a sorted CSV.

    python ./crawler.py > batteries.json
    python ./sorter.py < batteries.json

