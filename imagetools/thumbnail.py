#!/usr/bin/env python
import os
from subprocess import check_call

import struct
from imagetools.utils import get_image_format


def get_image_size(fpath):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    format_ = get_image_format(fpath)
    with open(fpath, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if format_ == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif format_ == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif format_ == 'jpg':
            try:
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception:  # IGNORE:W0703
                return
        else:
            return
        return width, height


def is_vertical(fpath):
    size = get_image_size(fpath)
    if size is None:
        return False
    else:
        width, heigth = size
        return False if width > heigth else True


def suggest_thumbnail_path(photo_path):
    photo_dir, photo_fname = os.path.split(photo_path)

    thumbnail_dir = os.path.join(photo_dir, 'thumbnails')
    if not os.path.exists(thumbnail_dir):
        os.mkdir(thumbnail_dir)
    thumbnail_path = os.path.join(thumbnail_dir, photo_fname)
    return thumbnail_path


def make_thumbnail(photo_path, thumbnail_fpath):
    if not os.path.exists(thumbnail_fpath):
        resize = 'x200' if is_vertical(photo_path) else '200'
        cmd = ['convert', '-thumbnail', resize, photo_path, thumbnail_fpath]
        check_call(cmd)
    else:
        print('thumbnail done {}'.format(thumbnail_fpath))
