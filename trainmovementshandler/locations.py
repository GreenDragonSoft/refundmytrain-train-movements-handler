#!/usr/bin/env python

"""
The Network Rail CORPUS data allows us to look up a location from the STANOX
code (which covers more than just public stations). It looks like
this:

```
{
    "TIPLOC": "LVRPLSH",
    "UIC": "22460",
    "NLCDESC16": " ",
    "STANOX": "36151",
    "NLC": "224600",
    "3ALPHA": "LIV",
    "NLCDESC": "LIVERPOOL LIME STREET"
}
```

The NAPTAN data set allows us to find human-friendly names and locations
by joining on the "three alpha" code. It looks like this:

```
{
    "GridType": "U",
    "Easting": "335100",
    "TiplocCode": "LVRPLSH",
    "CrsCode": "LIV",
    "ModificationDateTime": "2006-09-18T18:24:34",
    "StationNameLang": "",
    "StationName": "Liverpool Lime Street Rail Station",
    "Modification": "rev",
    "AtcoCode": "9100LVRPLSH",
    "CreationDateTime": "2003-11-04T00:00:00",
    "RevisionNumber": "1",
    "Northing": "390500"
}
```

"""

import json
import re

from collections import OrderedDict
from os.path import dirname, join as pjoin

CORPUS_FILENAME = pjoin(
    dirname(__file__), 'uk-train-data', 'db', 'network_rail_corpus.json'
)

NAPTAN_FILENAME = pjoin(
    dirname(__file__), 'uk-train-data', 'db', 'naptan_rail_locations.json'
)


class LookupError(KeyError):
    pass


class Location(object):
    """
    Reference data:
    http://nrodwiki.rockshore.net/index.php/Reference_Data
    """

    def __init__(self, corpus_record, naptan_record):
        """
        ```
        {
            "TIPLOC": "KETR",
            "UIC": "18570",
            "NLCDESC16": " ",
            "STANOX": "61009",
            "NLC": "185700",
            "3ALPHA": "KET",
            "NLCDESC": "KETTERING"
        },

        ```
        """

        self.corpus_record = corpus_record
        self.naptan_record = naptan_record

    @property
    def name(self):
        """
        http://nrodwiki.rockshore.net/index.php/NLC
        """
        if self.naptan_record is not None:
            return self.strip_trailing_rail_station(
                self.naptan_record['StationName'])
        else:
            return self.corpus_record['NLCDESC']

    @property
    def tiploc_code(self):
        """
        http://nrodwiki.rockshore.net/index.php/TIPLOC
        """
        return self._strip(self.corpus_record['TIPLOC'])

    @property
    def timing_point_location(self):
        return self._strip(self.tiploc)

    @property
    def uic_code(self):
        return self._strip(self.corpus_record['UIC'])

    @property
    def national_location_code(self):
        """
        http://nrodwiki.rockshore.net/index.php/NLC
        """
        return self._strip(self.corpus_record['NLC'])

    @property
    def stanox_code(self):
        return self._strip(self.corpus_record['STANOX'])

    @property
    def three_alpha(self):
        """
        A 3-character code used for stations. Previously referred to as CRS
        (Computer Reservation System) or NRS (National Reservation System)
        codes.
        eg: 'KET' (Kettering)
        """
        return self._strip(self.corpus_record['3ALPHA'])

    @property
    def crs_code(self):
        return self.three_alpha

    @property
    def is_public_station(self):
        return self.naptan_record is not None

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Location("{}")'.format(self.name)

    def serialize(self):
        return OrderedDict([
            ('name', self.name),
            ("stanox_code", self.stanox_code),
            ("three_alpha", self.three_alpha),
            ('is_public_station', self.is_public_station),
        ])

    @staticmethod
    def _strip(string):
        string = string.strip()
        return string if string != '' else None

    @staticmethod
    def strip_trailing_rail_station(string):
        return re.sub('(.*) Rail Station$', r'\1', string)


with open(NAPTAN_FILENAME, 'r') as f:
    NAPTAN_LOOKUP = {record['CrsCode']: record for record in json.load(f)}


with open(CORPUS_FILENAME, 'r') as f:
    def filter_empty_stanox(record):
        return record['STANOX'].strip() != ''

    LOCATIONS = [Location(record, NAPTAN_LOOKUP.get(record['3ALPHA']))
                 for record in filter(
                     filter_empty_stanox, json.load(f)['TIPLOCDATA'])]

    STANOX_LOOKUP = {loc.stanox_code: loc for loc in LOCATIONS}


def from_stanox(stanox):
    try:
        return STANOX_LOOKUP[stanox]
    except KeyError:
        raise LookupError('No location found for STANOX {}'.format(stanox))
