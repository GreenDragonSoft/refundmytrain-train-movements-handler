#!/usr/bin/env python

import json
import logging

from collections import OrderedDict
from os.path import dirname, join as pjoin

LOG = logging.getLogger(__name__)

OPERATING_COMPANIES_FN = pjoin(
    dirname(__file__), 'uk-train-data', 'db', 'operating_companies.json'
)

DELAY_REPAY_FN = pjoin(
    dirname(__file__), 'uk-train-data', 'db', 'delay_repay.json'
)


class OperatingCompany(object):
    """
    For a description of the different codes, see:
    http://nrodwiki.rockshore.net/index.php/TOC_Codes
    """

    def __init__(self, data):
        assert isinstance(data['numeric_code'], int), (
            "OperatingCompany instantiated with non-integer numeric "
            "code: `{}`".format(
                data['numeric_code']))

        self.name = data['name']
        self.business_code = data['business_code']
        self.numeric_code = data['numeric_code']
        self.atoc_code = data['atoc_code']

    def __str__(self):
        return '{} ({})'.format(self.name, self.atoc_code)

    def __repr__(self):
        return 'OperatingCompany("{}")'.format(self.name)

    def serialize(self):
        return OrderedDict([
            ('name', self.name),
            ("business_code", self.business_code),
            ('numeric_code', self.numeric_code),
            ('atoc_code', self.atoc_code),
        ])

    @property
    def delay_repay_policy(self):
        return DELAY_REPAY.get(self.atoc_code, None)

    def is_delay_repay_eligible(self, late_minutes):
        policy = self.delay_repay_policy

        if policy is None:
            LOG.warning('No delay repay policy for {}'.format(self))
            return False
        else:
            return policy.is_eligible(late_minutes)


class DelayRepayPolicy(object):
    """
    Calculates the amount of compensation due for a given lateness of a train.
    """

    def __init__(self, record):
        self.minimum_eligible_minutes = record['minimum_minutes']

    def is_eligible(self, late_minutes):
        if self.minimum_eligible_minutes is None:
            return False

        return late_minutes >= self.minimum_eligible_minutes


with open(OPERATING_COMPANIES_FN, 'r') as f:
    OPERATING_COMPANIES = [OperatingCompany(record) for record in json.load(f)]
    BUSINESS_CODE_LOOKUP = {oc.business_code: oc for oc in OPERATING_COMPANIES}
    NUMERIC_CODE_LOOKUP = {oc.numeric_code: oc for oc in OPERATING_COMPANIES}
    ATOC_CODE_LOOKUP = {oc.atoc_code: oc for oc in OPERATING_COMPANIES}


with open(DELAY_REPAY_FN, 'r') as f:
    DELAY_REPAY = {record['atoc_code']: DelayRepayPolicy(record)
                   for record in json.load(f)}


def from_business_code(business_code):
    return BUSINESS_CODE_LOOKUP[business_code]


def from_numeric_code(numeric_code):
    if not isinstance(numeric_code, int):
        raise TypeError('Numeric code should be int, got {} `{}`'.format(
            type(numeric_code), numeric_code))

    return NUMERIC_CODE_LOOKUP[numeric_code]


def from_atoc_code(atoc_code):
    return ATOC_CODE_LOOKUP[atoc_code]
