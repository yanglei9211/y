#!/usr/bin/env python
# encoding: utf-8

from pymongo import MongoClient


def main():
    db = MongoClient('127.0.0.1', 27017)['test']
    print "creating needed indexes..."

    db.upload_history.ensure_index(
        [('file_name', 1)],
        unique=True
    )


if __name__ == "__main__":
    main()
