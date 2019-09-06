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
import jsondiff
import click

from datadiff.diff import bsondiff, jsondiff, csvdiff
from datadiff.delta import apply_json_diff, json_delta

@click.group()
def cli1():
    pass

@cli1.command()
@click.argument('key')
@click.argument('left')
@click.argument('right')
def compare(key, left, right):
    import sys
    ext = left.rsplit('.', 1)[-1]
    if ext == 'bson':
        report = bsondiff(key, left, right)
    elif ext in ['json', 'jsonl']:
        report = jsondiff(key, left, right)
    elif ext == 'csv':
        report = csvdiff(key, left, right)
    else:
        print('Wrong file extension: bson, json or csv supported')
        sys.exit(1)
    stats = {'a' : len(report['a']),
             'c' : len(report['c']),
             'd' : len(report['d'])}

    print('%-12i records added' % (stats['a']))
    print('%-12i records changed' % (stats['c']))
    print('%-12i records deleted' % (stats['d']))


@click.group()
def cli2():
    pass

@cli2.command()
@click.argument('key')
@click.argument('left')
@click.argument('right')
@click.argument('output')
def delta(key, left, right, output):
    ext = left.rsplit('.', 1)[-1]
    if ext == 'json':
        deltafile = output
        outfile = open(deltafile, 'w', encoding='utf8')
        json_delta(key, left, right, outfile, difftype='full')
    pass

@click.group()
def cli3():
    pass

@cli3.command()
@click.argument('dataset')
@click.argument('delta')
@click.argument('output')
def patch(dataset, delta, output):
    outfile = open(output, 'w', encoding='utf8')
    apply_json_delta(dataset, delta, outfile)


cli = click.CommandCollection(sources=[cli1, cli2, cli3])

if __name__ == '__main__':
    cli()

