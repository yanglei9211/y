#!/usr/bin/env python
# encoding: utf-8

import json
from bson import ObjectId
from bson.errors import InvalidId
from tornado.web import HTTPError
import tornado.escape

json_decode = tornado.escape.json_decode


def safe_objectid_from_str(value):
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPError(400, "bad object id")


def safe_typed_from_str(value, type_):
    try:
        return type_(value)
    except:
        raise HTTPError(400, "'%s' is not a '%s'" %
                        (value, value.__class__.__name__))


def safe_json_decode(value):
    try:
        return json_decode(value)
    except ValueError:
        raise HTTPError(400, 'bad string for json')


def json_encode(value, ensure_ascii=False, indent=None):
    def objectid_encoder(obj):
        type_encoders = [
            (ObjectId, str),
        ]
        for encoder in type_encoders:
            if isinstance(obj, encoder[0]):
                return encoder[1](obj)
        raise TypeError("Unknown value '%s' of type %s" % (
            obj, type(obj)))
    # adapted from tornado.escape.json_encode
    return json.dumps(
        value, default=objectid_encoder,
        ensure_ascii=ensure_ascii,
        indent=indent).replace("</", "<\\/")
