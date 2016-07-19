#!/usr/bin/env python

import csv
import os
import json
import sys
import shutil
import argparse

from imagetools.utils.utils import (RandomNameSequence, add_json_metadata,
                                    is_image)
from gi.repository import GExiv2


NAMER = RandomNameSequence()


def parse_plants(fhand, plant_part=None, assay=None):
    plants = {}
    for plant in csv.DictReader(fhand, delimiter=','):
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


def _get_metadata(fpath):
    exif = GExiv2.Metadata(fpath)
    metadata = json.loads(exif["Exif.Photo.UserComment"])
    if "img_id" not in metadata:
        msg = "Image doesn't have an Image_ID"
        raise ValueError(msg)
    if "plant_id" not in metadata:
        msg = "Image doesn't have an Unique_ID"
        raise ValueError(msg)
    return metadata


def define_arguments():
    parser = argparse.ArgumentParser(description='Arrange basic photos by accession')
    parser.add_argument('--in_dir', '-i', metavar='fpath', dest='in_fpath',
                        type=str, help='FilePath with photos to be arranged')
    parser.add_argument('--CSV', '-c', metavar='csv', dest='csv',
                        type=argparse.FileType('r'),
                        help='CSV with additional info to insert')
    parser.add_argument('--out_dir', '-o', metavar='fpath', dest='out_fpath',
                        type=str, help='FilePath for arranged photos')
    args = parser.parse_args()
    return args


def main():
    args = define_arguments()
    if os.path.exists(args.out_fpath):
        raise RuntimeError('The output directory exists')
    os.mkdir(args.out_fpath)
    plants = parse_plants(args.csv)
    for fname in os.listdir(args.in_fpath):
        fhand = os.path.abspath(os.path.join(args.in_fpath, fname))
        if is_image(fhand):
            metadata = _get_metadata(fhand)
            plant_info = plants[metadata["plant_id"]]
            plant_info.update(metadata)
            out_fpath = _copy_file(fhand, args.out_fpath, plant_info)
            add_json_metadata(plant_info, out_fpath)

if __name__ == '__main__':
    main()
