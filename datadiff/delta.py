#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Data differ code
__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "MIT"

from .diff import bsondiff, bson_index, compare_index, json_index, csv_index
import io
import bson
import json
import csv
import xxhash


# import jsondiff


def json_delta(key, left, right, outfile, difftype="full"):
    """Generates delta file against 2 jsonl (json lines) files with 'key' as unique key of each record"""
    complexkey = False
    if key.find(".") > -1:
        parts = key.split(".")
        complexkey = True

    if isinstance(left, io.IOBase):
        leftf = left
    else:
        leftf = open(left, "r", encoding="utf8")

    if isinstance(right, io.IOBase):
        rightf = right
    else:
        rightf = open(right, "r", encoding="utf8")

    lefti = json_index(key, leftf)
    righti = json_index(key, rightf)
    report = compare_index(lefti, righti)
    n = 0
    n2 = 0
    leftf.seek(0)
    rightf.seek(0)
    ldiffed = {}
    rdiffed = {}
    output = {"uniqkey": key, "records": []}
    for line in rightf:
        r = json.loads(line)
        if not complexkey:
            kv = r[key]
        else:
            v = r
            for p in parts:
                v = v[p]
            kv = v
        if kv in report["a"]:
            o = {"mode": "a", "uniqkey": kv, "obj": r}
            output["records"].append(o)
            n += 1
        elif kv in report["c"]:
            ldiffed[kv] = r
            #            o = {'mode' : 'c', 'uniqkey' : key, 'obj': r}
            #            outfile.write(json.dumps(o)+'\n')
            n2 += 1
    n = 0
    for line in leftf:
        r = json.loads(line)
        if not complexkey:
            kv = r[key]
        else:
            v = r
            for p in parts:
                v = v[p]
            kv = v
        if kv in report["d"]:
            n += 1
            o = {"mode": "d", "uniqkey": kv, "obj": r}
            output["records"].append(o)
        elif kv in report["c"]:
            rdiffed[kv] = r
    for key in report["c"]:
        kv = key
        if difftype == "patch":
            #            patch = jsondiff.diff(rdiffed[key], ldiffed[key], syntax='explicit', dump=True)
            #            o = {'mode' : 'c', 'uniqkey' : kv, 'patch': patch}
            Exception("not supported yet")
        else:
            o = {"mode": "c", "uniqkey": kv, "obj": ldiffed[key]}
        output["records"].append(o)
        pass
    outfile.write(json.dumps(output, indent=4))
    return outfile


def apply_json_delta(left, patch, outfile):
    """Apply patch to JSON lines file"""
    if isinstance(left, io.IOBase):
        leftf = left
    else:
        leftf = open(left, "r", encoding="utf8")

    if isinstance(patch, io.IOBase):
        deltaf = patch
    else:
        deltaf = open(patch, "r", encoding="utf8")
    patchdata = json.load(deltaf)
    patched = {"a": {}, "c": {}, "d": {}}
    for r in patchdata["records"]:
        if "patch" in r.keys():
            o = r["patch"]
        else:
            o = r["obj"]
        patched[r["mode"]][r["uniqkey"]] = o
    for line in leftf:
        o = json.loads(line)
        if o[patchdata["uniqkey"]] in patched["d"]:
            continue
        elif o[patchdata["uniqkey"]] in patched["c"]:
            o = patched["c"][o[patchdata["uniqkey"]]]
            outfile.write(json.dumps(o) + "\n")
        else:
            outfile.write(json.dumps(o) + "\n")
    for o in patched["a"].values():
        outfile.write(json.dumps(o) + "\n")


def bson_delta(key, left, right, outfile, difftype="full"):
    """Generates delta file against 2 BSON files with 'key' as unique key of each record"""
    complexkey = False
    if key.find(".") > -1:
        parts = key.split(".")
        complexkey = True

    if isinstance(left, io.IOBase):
        leftf = left
    else:
        leftf = open(left, "rb", encoding="utf8")

    if isinstance(right, io.IOBase):
        rightf = right
    else:
        rightf = open(right, "rb", encoding="utf8")

    lefti = bson_index(key, leftf)
    righti = bson_index(key, rightf)
    report = compare_index(lefti, righti)
    n = 0
    n2 = 0
    leftf.seek(0)
    rightf.seek(0)
    ldiffed = {}
    rdiffed = {}
    output = {"uniqkey": key, "records": []}
    for line in rightf:
        r = json.loads(line)
        if not complexkey:
            kv = r[key]
        else:
            v = r
            for p in parts:
                v = v[p]
            kv = v
        if kv in report["a"]:
            o = {"mode": "a", "uniqkey": kv, "obj": r}
            output["records"].append(o)
            n += 1
        elif kv in report["c"]:
            ldiffed[kv] = r
            #            o = {'mode' : 'c', 'uniqkey' : key, 'obj': r}
            #            outfile.write(json.dumps(o)+'\n')
            n2 += 1
    n = 0
    for line in leftf:
        r = json.loads(line)
        if not complexkey:
            kv = r[key]
        else:
            v = r
            for p in parts:
                v = v[p]
            kv = v
        if kv in report["d"]:
            n += 1
            o = {"mode": "d", "uniqkey": kv, "obj": r}
            output["records"].append(o)
        elif kv in report["c"]:
            rdiffed[kv] = r
    for key in report["c"]:
        kv = key
        if difftype == "patch":
            #            patch = jsondiff.diff(rdiffed[key], ldiffed[key], syntax='explicit', dump=True)
            #            o = {'mode' : 'c', 'uniqkey' : kv, 'patch': patch}
            pass
        else:
            o = {"mode": "c", "uniqkey": kv, "obj": ldiffed[key]}
        output["records"].append(o)
        pass
    outfile.write(bson.BSON.encode(output))
    return outfile


def apply_bson_delta(left, patch, outfile):
    """Apply patch to bson file and output results file"""
    if isinstance(left, io.IOBase):
        leftf = left
    else:
        leftf = open(left, "rb")

    if isinstance(patch, io.IOBase):
        deltaf = patch
    else:
        deltaf = open(patch, "rb")

    patchdata = bson.decode(deltaf.read())
    patched = {"a": {}, "c": {}, "d": {}}
    for r in patchdata["records"]:
        if "patch" in r.keys():
            o = r["patch"]
        else:
            o = r["obj"]
        patched[r["mode"]][r["uniqkey"]] = o
    for o in bson.decode_file_iter(leftf):
        if o[patchdata["uniqkey"]] in patched["d"]:
            continue
        elif o[patchdata["uniqkey"]] in patched["c"]:
            o = patched["c"][o[patchdata["uniqkey"]]]
            outfile.write(bson.BSON.encode(o))
        else:
            outfile.write(bson.BSON.encode(o))
    for o in patched["a"].values():
        outfile.write(bson.BSON.encode(o))


def csv_delta(key, left, right, outfile, difftype="full", sep=","):
    """Generates delta file against 2 CSV files with 'key' as unique key of each record"""
    complexkey = False
    if key.find(".") > -1:
        parts = key.split(".")
        complexkey = True

    if isinstance(left, io.IOBase):
        leftf = left
    else:
        leftf = open(left, "r", encoding="utf8")

    if isinstance(right, io.IOBase):
        rightf = right
    else:
        rightf = open(right, "r", encoding="utf8")

    lefti = csv_index(key, leftf)
    righti = csv_index(key, rightf)
    report = compare_index(lefti, righti)
    n = 0
    n2 = 0
    leftf.seek(0)
    rightf.seek(0)
    ldiffed = {}
    rdiffed = {}
    output = {"uniqkey": key, "records": []}
    rightr = csv.reader(rightf, delimiter=sep)
    for line in rightr:
        r = line
        if not complexkey:
            kv = r[key]
        else:
            v = r
            for p in parts:
                v = v[p]
            kv = v
        if kv in report["a"]:
            o = {"mode": "a", "uniqkey": kv, "obj": r}
            output["records"].append(o)
            n += 1
        elif kv in report["c"]:
            ldiffed[kv] = r
            #            o = {'mode' : 'c', 'uniqkey' : key, 'obj': r}
            #            outfile.write(json.dumps(o)+'\n')
            n2 += 1
    n = 0
    leftr = csv.reader(leftf, delimiter=sep)
    for line in leftr:
        r = line
        if not complexkey:
            kv = r[key]
        else:
            v = r
            for p in parts:
                v = v[p]
            kv = v
        if kv in report["d"]:
            n += 1
            o = {"mode": "d", "uniqkey": kv, "obj": r}
            output["records"].append(o)
        elif kv in report["c"]:
            rdiffed[kv] = r
    for key in report["c"]:
        kv = key
        if difftype == "patch":
            #            patch = jsondiff.diff(rdiffed[key], ldiffed[key], syntax='explicit', dump=True)
            #            o = {'mode' : 'c', 'uniqkey' : kv, 'patch': patch}
            pass
        else:
            o = {"mode": "c", "uniqkey": kv, "obj": ldiffed[key]}
        output["records"].append(o)
        pass
    outfile.write(json.dumps(output, indent=4))
    return outfile


if __name__ == "__main__":
    import sys

    ext = sys.argv[1].rsplit(".", 1)[-1]
    if ext == "json":
        deltafile = sys.argv[1].rsplit(".", 1)[0] + "_delta.json"
        outfile = open(deltafile, "w", encoding="utf8")
        json_delta(sys.argv[3], sys.argv[1], sys.argv[2], outfile, difftype="full")
    elif ext == "csv":
        deltafile = sys.argv[1].rsplit(".", 1)[0] + "_delta.json"
        print(deltafile)
        outfile = open(deltafile, "w", encoding="utf8")
        csv_delta(sys.argv[3], sys.argv[1], sys.argv[2], outfile, difftype="full")
