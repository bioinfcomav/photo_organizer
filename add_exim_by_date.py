#!/usr/bin/env python

import datetime
import os
import shutil
import sys
import json
from random import Random

from gi.repository import GExiv2


class RandomNameSequence:
    """An instance of _RandomNameSequence generates an endless
    sequence of unpredictable strings which can safely be incorporated
    into file names.  Each string is six characters long.  Multiple
    threads can safely use the same instance at the same time.

    _RandomNameSequence is an iterator."""

    characters = "abcdefghijklmnopqrstuvwxyz0123456789"

    @property
    def rng(self):
        cur_pid = os.getpid()
        if cur_pid != getattr(self, '_rng_pid', None):
            self._rng = Random()
            self._rng_pid = cur_pid
        return self._rng

    def __iter__(self):
        return self

    def __next__(self):
        c = self.characters
        choose = self.rng.choice
        letters = [choose(c) for dummy in range(8)]
        return ''.join(letters)

NAMER = RandomNameSequence()


def sort_by_metadata_creation_time(dir_fnames):
    fpaths = []
    for fname in os.listdir(dir_fnames):
        fpath = os.path.join(dir_fnames, fname)
        if os.path.isfile(fpath):
            date = GExiv2.Metadata(fpath)["Exif.Image.DateTime"]
            fpaths.append({"fpath": fpath, "date": date,
                           "metadata": GExiv2.Metadata(fpath)["Exif.Photo.UserComment"]})
    fpaths.sort(key=lambda x: datetime.datetime.strptime(x['date'],
                '%Y:%m:%d %H:%M:%S'))
    return fpaths


def add_json_metadata(plant, fpath):
    exif = GExiv2.Metadata(fpath)
    json_plant_info = json.dumps(plant, sort_keys=True)
    exif["Exif.Photo.UserComment"] = json_plant_info
    exif.save_file()


def _copy_file(fpath, out_dir, plant_info):
    image_dest_dir = os.path.join(out_dir, plant_info['Accession'])
    if not os.path.exists(image_dest_dir):
        os.mkdir(image_dest_dir)
    if sys.version_info[0] < 3:
        random_code = NAMER.__next__()
    else:
        random_code = next(NAMER)
    fname = '{}_{}_{}.jpg'.format(plant_info['plant_id'],
                                  plant_info['plant_part'], random_code)
    dest_fpath = os.path.join(image_dest_dir, fname)
    shutil.copy2(fpath, dest_fpath)
    return dest_fpath


def test():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(SCRIPT_DIR, "test_date_images")
    dir_fnames = sort_by_metadata_creation_time(test_dir)
    assert dir_fnames[-1]["fpath"] == os.path.join(test_dir,
                                                   "tomato_plant.jpg")
    assert not dir_fnames[-1]["metadata"]
    out_fdir = os.path.join(SCRIPT_DIR, "out_date_test")
    os.mkdir(out_fdir)
    for fname in dir_fnames:
        if fname["metadata"]:
            metadata_qr = fname["metadata"]
            out_fpath = _copy_file(fname["fpath"], out_fdir,
                                   json.loads(metadata_qr))
        else:
            out_fpath = _copy_file(fname["fpath"], out_fdir,
                                   json.loads(metadata_qr))
            add_json_metadata(json.loads(metadata_qr), out_fpath)
    dir_fnames = sort_by_metadata_creation_time(os.path.join(out_fdir,
                                                             "BGV012627"))
    assert dir_fnames[-2]["metadata"] == dir_fnames[-1]["metadata"]
    assert dir_fnames[0]["metadata"] != dir_fnames[-1]["metadata"]
    shutil.rmtree(out_fdir)


def main():
    dir_fnames = sort_by_metadata_creation_time(sys.argv[1])
    out_dir = sys.argv[2]
    if os.path.exists(out_dir):
        raise RuntimeError('The output directory exists')
    os.mkdir(out_dir)
    for fname in dir_fnames:
        if fname["metadata"]:
            metadata_qr = fname["metadata"]
            out_fpath = _copy_file(fname["fpath"], out_dir,
                                   json.loads(metadata_qr))
        else:
            out_fpath = _copy_file(fname["fpath"], out_dir,
                                   json.loads(metadata_qr))
            add_json_metadata(json.loads(metadata_qr), out_fpath)

if __name__ == '__main__':
    test()
    main()
