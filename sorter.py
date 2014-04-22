

class Sorter:

    def __init__(self, results, **kwargs):
        self.UNSORTED = filter(None, results)
        self.SORTED = []


    # Sort by mWh/ $
    def sort(self):
        for i, pack in enumerate(self.UNSORTED):
            volts = float(pack['cells']) * 3.7
            mWatts = volts * float(pack['capacity'])
            wh_per_dollar = float(pack['price'].replace('$', '')) / (mWatts / 1000)
            self.UNSORTED[i]['wh_per_dollar'] = round(wh_per_dollar, 5)

        self.SORTED = sorted(self.UNSORTED, key=lambda pack:pack['wh_per_dollar'])


if __name__ == '__main__':
    import csv
    import json
    import sys

    _json = ''

    for line in sys.stdin:
        _json += line

    sorter = Sorter(json.loads(_json))
    sorter.sort()

    # Write csv out
    writer = csv.writer(sys.stdout)
    headers = ('Price', 'Cells', 'Capacity (mAh)', 'Dollars per Wh', 'Link')
    writer.writerow(headers)
    for pack in sorter.SORTED:
        row = (pack['price'], pack['cells'], pack['capacity'], pack['wh_per_dollar'], pack['link'])
        writer.writerow(row)

