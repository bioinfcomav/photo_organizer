#!/usr/bin/env python

import csv
import os
import json
import sys
import shutil
from random import Random
from tempfile import NamedTemporaryFile

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


def parse_plants(fpath, plant_part=None, assay=None):
    plants = {}
    for plant in csv.DictReader(open(fpath), delimiter=','):
            if 'unique_id' in plant:
                plant['plant_id'] = plant['unique_id']
                plant.pop('unique_id', None)
            if plant['Accession'] == 'UNKNOWN':
                plant['Accession'] = plant['Synonym']
            if plant_part is not None:
                plant['plant_part'] = plant_part
            if assay is not None:
                plant['assay'] = assay
            plant_id = plant['plant_id']
            plants[plant_id] = plant
    return plants


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


def main():
    in_fhand = open(sys.argv[1])
    out_dir = sys.argv[2]
    plant_part = sys.argv[3]
    assay = sys.argv[4]
    if os.path.exists(out_dir):
        raise RuntimeError('The output directory exists')

    os.mkdir(out_dir)
    plants = parse_plants(PLANTS[assay], plant_part, assay)
    for entry in csv.DictReader(in_fhand, delimiter=','):
        fpath = entry['fpath']
        code = entry['plant_id']
        plant_info = plants[code]
        out_fpath = _copy_file(fpath, out_dir, plant_info)
        add_json_metadata(plant_info, out_fpath)


def test():
    assay = 'NSF1'
    plant_part = 'Leaf'
    plants = parse_plants(PLANTS[assay], plant_part, assay)
    image1_path = os.path.join(SCRIPT_DIR, 'test_images/IMG_1262.JPG')
    code = '0F16NSF1CN02F01M004'
    out_fhand = NamedTemporaryFile(suffix='jpg')
    plant_info = plants[code]
    assert 'unique_id' not in plant_info
    assert 'plant_id' in plant_info
    shutil.copyfileobj(open(image1_path), out_fhand)
    out_fhand.flush()
    add_json_metadata(plant_info, out_fhand.name)
    exif = GExiv2.Metadata(out_fhand.name)
    exif_comments = exif.get_comment()
    assert json.loads(exif_comments) == {"Accession": "BGV007181",
                                         "Synonym": "ECU1421",
                                         "assay": "NSF1", "exp_field": "CN02",
                                         "plant_part": "Leaf", "row": "1",
                                         "replica": "1", "pot_number": "4",
                                         "plant_id": "0F16NSF1CN02F01M004"}


if __name__ == '__main__':
    # TODO: REDO TEST
    main()
