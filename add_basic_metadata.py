#!/usr/bin/env python

import csv
import os
import json
import sys
import shutil
from random import Random

from gi.repository import GExiv2

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLANTS = {'NSF1': os.path.join(SCRIPT_DIR, 'NSF1_plants.csv'),
          'NSF2': os.path.join(SCRIPT_DIR, 'NSF2_plants.csv')}


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


def add_json_metadata(plant_info, fpath):
    exif = GExiv2.Metadata(fpath)
    json_plant_info = json.dumps(plant_info, sort_keys=True)
    exif["Exif.Photo.UserComment"] = json_plant_info
    exif.save_file()


def _copy_file(fpath, out_dir, plant_info):
    if sys.version_info[0] < 3:
        random_code = NAMER.__next__()
    else:
        random_code = next(NAMER)
    fname = '{}_{}_{}.jpg'.format(plant_info['plant_id'],
                                  plant_info['plant_part'],
                                  random_code)
    dest_fpath = os.path.join(out_dir, fname)
    shutil.copy2(fpath, dest_fpath)
    return dest_fpath


def main():
    in_fhand = open(sys.argv[1])
    out_dir = sys.argv[2]
    plant_part = sys.argv[3]

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    for entry in csv.DictReader(in_fhand, delimiter=','):
        fpath = entry['fpath']
        plant_info = {"plant_id": entry['plant_id'],
                      "img_id": entry['image_id'],
                      "assay": entry['assay'],
                      "project": entry['project'],
                      "plant_part": plant_part}
        out_fpath = _copy_file(fpath, out_dir, plant_info)
        add_json_metadata(plant_info, out_fpath)


if __name__ == '__main__':
    main()
