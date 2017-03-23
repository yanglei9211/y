#!/usr/bin/env python
# encoding: utf-8

import os
import hashlib
import shutil


def path_prefix(file_name):
    return os.path.join(file_name[:2], file_name[2:4])


def fullpath(root, file_name):
    return os.path.join(root, path_prefix(file_name), file_name)


def data_open(root, file_name):
    path = os.path.join(root, path_prefix(file_name), file_name)
    return open(path, "rb")


def ensure_dir_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)


def data_save(root, content, ext=""):
    digest = hashlib.md5(content).hexdigest()
    path_name = fullpath(root, digest)
    if ext:
        if ext.startswith('.'):
            path_name += ext
        else:
            path_name += '.' + ext

    abspath = os.path.abspath(path_name)
    if os.path.exists(abspath):
        return os.path.basename(abspath)

    dirname = os.path.dirname(abspath)
    ensure_dir_exist(dirname)

    tmp_abspath = '{}.tmp.{}'.format(abspath, os.getpid())
    with open(tmp_abspath, "wb") as fobj:
        fobj.write(content)
    shutil.move(tmp_abspath, abspath)
    return os.path.basename(abspath)
