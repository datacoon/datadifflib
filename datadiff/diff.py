#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Data differ code
__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "MIT"

import io
import bson
import json
import csv
import xxhash


def csv_index(key, csvf, delimiter=';'):
    """Index csv file records and return dict with key and hash of record"""
    bindex = {}
    reader = csv.DictReader(csvf, delimiter=delimiter)
    for r in reader:
        rh = xxhash.xxh64(str(r)).hexdigest()
        bindex[r[key]] = rh
    return bindex

def json_index(key, jsonf):
    """Index json file records and return dict with key and hash of each record"""
    bindex = {}
    complexkey = False
    if key.find('.') > -1:
        parts = key.split('.')
        complexkey = True
    for l in jsonf:
        r = json.loads(l)
        rh = xxhash.xxh64(bson.BSON.encode(r)).hexdigest()
        if not complexkey:
            bindex[r[key]] = rh
        else:
            v = r
            for p in parts:
                v = v[p]
            bindex[v] = rh
    return bindex


def bson_index(key, bsonf):
    """Index bson file records and return dict with key and hash of each record"""

    bindex = {}
    for r in bson.decode_file_iter(bsonf):
        rh = xxhash.xxh64(bson.BSON.encode(r)).hexdigest()
#        rh = xxhash.xxh64(str(r)).intdigest()
        bindex[r[key]] = rh
    return bindex

def dict_index(key, arr):
    """Index python dict records and return dict with key and hash of each record"""
    bindex = {}
    for r in arr:
        rh = xxhash.xxh64(str(r)).hexdigest()
        bindex[r[key]] = rh
    return bindex


def compare_index(lefti, righti):
    """Compares to indexes and returns dict with all added, removed and changed records"""
    setl = set(lefti.keys())
    setr = set(righti.keys())
    diffl = setl.difference(setr)
    diffr = setr.difference(setl)
    inter = setl.intersection(setr)
    changed = []
    for i in inter:
        if lefti[i] != righti[i]:
            changed.append(i)
    report = {'a' : [], 'c' : [], 'd' : []}
    for i in diffr:
        report['a'].append(i)
    for i in diffl:
        report['d'].append(i)
    for i in changed:
        report['c'].append(i)
    return report

def basediff(key, left, right, difftype='csv'):
    """Generates diff report between left and right files"""
    if isinstance(left, io.IOBase):
        leftf = left
    elif difftype == 'csv':
        leftf = open(left, 'r', encoding='utf8')
    else:
        leftf = open(left, 'rb')

    if isinstance(right, io.IOBase):
        rightf = right
    elif difftype == 'csv':
        rightf = open(right, 'r', encoding='utf8')
    else:
        rightf = open(right, 'rb')

    if difftype == 'csv':
        lefti = csv_index(key, leftf)
        righti = csv_index(key, rightf)
    elif difftype == 'bson':
        lefti = bson_index(key,  leftf)
        righti = bson_index(key,  rightf)
    elif difftype == 'json':
        lefti = json_index(key,  leftf)
        righti = json_index(key,  rightf)
    else:
        return None
    report = compare_index(lefti, righti)
    return report

def bsondiff(key, left, right):
    """Returns difference between two bson files by selected unique key"""
    return basediff(key, left, right, difftype='bson')

def jsondiff(key, left, right):
    """Returns difference between two json files by selected unique key"""
    return basediff(key, left, right, difftype='json')

def csvdiff(key, left, right):
    """Returns difference between two csv files by selected unique key"""
    return basediff(key, left, right, difftype='csv')


def arrdiff(key, left, right):
    """Returns difference between two arrays of dicts. Each array record should be dict with unique id defined in 'key' variable"""
    lefti = dict_index(key, left)
    righti = dict_index(key, right)
    return compare_index(lefti, righti)



if __name__ == "__main__":
    import sys
    ext = sys.argv[1].rsplit('.', 1)[-1]
    if ext == 'bson':
        report = bsondiff(sys.argv[3], sys.argv[1], sys.argv[2])
    elif ext in ['json', 'jsonl']:
        report = jsondiff(sys.argv[3], sys.argv[1], sys.argv[2])
    elif ext == 'csv':
        report = csvdiff(sys.argv[3], sys.argv[1], sys.argv[2])
    else:
        print('Wrong file extension: bson, json or csv supported')
        sys.exit(1)
    stats = {'a' : len(report['a']),
             'c' : len(report['c']),
             'd' : len(report['d'])}

    print(json.dumps(stats, indent=4))
