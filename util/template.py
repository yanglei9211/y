#!/usr/bin/env python
# fileencoding=utf-8
import datetime

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import BytecodeCache


from escape import json_encode


def _ts_format(ts, format=None):
    dt = datetime.datetime.fromtimestamp(ts)
    if format is None:
        return dt.strftime("%m-%d %H:%M")
    elif format == 'absolute':
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif format == 'onlydate':
        return dt.strftime("%m-％d")
    elif format == 'fulldata':
        return dt.strftime("%Y-%m-%d")
    elif format == 'ym':
        return dt.strftime(u'%Y年%m月')
    else:
        return dt.strftime(format)

ts_format = _ts_format


class MemoryBytecodeCache(BytecodeCache):
    def __init__(self):
        self.cache = {}

    def load_bytecode(self, bucket):
        code = self.cache.get(bucket)
        if code:
            bucket.bytecode_from_string(code)

    def dump_bytecode(self, bucket):
        self.cache[bucket.key] = bucket.bytecode_to_string()

    def clear(self):
        self.cache = {}


class JinjaLoader(object):
    def __init__(self, **kwargs):
        super(JinjaLoader, self).__init__()
        auto_reload = kwargs.get('debug', True)
        loader = kwargs.get('loader')
        if not loader:
            root_path = kwargs.get('root_path')
            if not root_path:
                assert 'no loader could be selected!'
            loader = FileSystemLoader(root_path)
        auto_escape = False
        self.env = Environment(loader=loader,
                               autoescape=auto_escape,
                               extensions=['jinja2.ext.autoescape'],
                               trim_blocks=True,
                               cache_size=-1,
                               bytecode_cache=MemoryBytecodeCache(),
                               auto_reload=auto_reload
                               )
        additional_globals = {
            'ord': ord,
            'chr': chr,
            'unichr': unichr,
            'json_encode': json_encode,
        }
        self.env.globals.update(additional_globals)
        self.env.filters['ts_format'] = _ts_format

    def load(self, name):
        return JinjaTemplate(self.env.get_template(name))

    def reset(self):
        self.env.cache.clear()


class JinjaTemplate(object):
    def __init__(self, template):
        self.template = template

    def generate(self, **kwargs):
        return self.template.render(**kwargs).encode('utf-8')


