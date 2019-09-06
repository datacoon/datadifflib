====================================================
datadiff -- library and tool to compare data files JSON, CSV and BSON and to create and apply changes between dataset versions
====================================================

.. image:: https://img.shields.io/travis/datacoon/datadifflib/master.svg?style=flat-square
    :target: https://travis-ci.org/ivbeg/qddate
    :alt: travis build status

.. image:: https://img.shields.io/pypi/v/datadifflib.svg?style=flat-square
    :target: https://pypi.python.org/pypi/datadifflib
    :alt: pypi version

.. image:: https://readthedocs.org/projects/datadifflib/badge/?version=latest
    :target: http://datadifflib.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status



`datadifflib` is a Python 3 lib that helps track changes between two versions of dataset and to produce delta file of changes of these files.
It supports JSON, BSON and CSV file formats and could produce delta files for each of these data formats.



Documentation
=============

Documentation is built automatically and can be found on
`Read the Docs <https://datadifflib.readthedocs.org/en/latest/>`_.


Features
========

* As simple as possible
* Minimalistic memory footprint
* File formats supported: BSON, JSON, CSV


Limitations
========

* Only JSON files supported to generate and apply delta files
* Limited support for very huge files 100GB+, max tested files are 5GB
* Files readed twice to generated delta. First time it generates index and second time it extracts added, deleted and changed records




Command-line tool
=================
Usage: datadiffcli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
* compare   Compares records in two files with unique key and returns if changes exists
* delta     Generates delta file
* patch     Applies patch from delta file

Examples
========

Compare two versions of same dataset with unique key defined in 'regnum' field in each dataset

    python datadiffcli.py compare regnum reestrgp_2018.json reestrgp_2019.json  
    
Generates delta file after comparsion of two versions of same dataset with unique key defined in 'regnum' field
                                                                                          
    python datadiffcli.py delta regnum reestrgp_2018.json reestrgp_2019.json reestrgp_delta.json 

Apply delta file against original dataset and produce updated dataset

    python datadiffcli.py patch reestrgp_2018.json reestrgp_delta.json reestrgp_proc.json 


How to use library
==================

Generates report on changes between 'reestrgp_2018.json' and 'reestrgp_2019.json' versions of dataset with unique key 'regnum'
    >>> from datadiff.diff import jsondiff
    >>> key = 'regnum'
    >>> left = 'reestrgp_2018.json'
    >>> right = 'reestrgp_2019.json'
    >>> report = jsondiff(key, left, right)


Generates delta file between two versions of dataset	
    >>> from datadiff.delta import json_delta
    >>> left = 'reestrgp_2018.json'
    >>> right = 'reestrgp_2019.json'
    >>> outfile = 'reestrgp_delta.json'
    >>> json_delta(key, left, right, outfile, difftype='full')


Apply patch to first version of dataset	
    >>> from datadiff.delta import apply_json_delta
    >>> dataset = 'reestrgp_2018.json'
    >>> delta = 'reestrgp_delta.json'
    >>> outfile = 'reestrgp_proc.json'
    >>> apply_json_delta(key, dataset, delta, outfile)

                                                                                                                         
