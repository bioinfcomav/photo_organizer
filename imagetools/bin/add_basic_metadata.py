#!/usr/bin/env python

import csv
import os
import shutil
import argparse
from imagetools.utils.utils import RandomNameSequence, add_json_metadata


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLANTS = {'NSF1': os.path.join(SCRIPT_DIR, 'NSF1_plants.csv'),
          'NSF2': os.path.join(SCRIPT_DIR, 'NSF2_plants.csv')}

NAMER = RandomNameSequence()


def _copy_file(fpath, out_dir, plant_info):
    random_code = next(NAMER)
    fname = '{}_{}_{}.jpg'.format(plant_info['plant_id'],
                                  plant_info['plant_part'],
                                  random_code)
    dest_fpath = os.path.join(out_dir, fname)
    shutil.copy2(fpath, dest_fpath)
    return dest_fpath


def define_arguments():
    parser = argparse.ArgumentParser(description='Add basic metadata to images')
    parser.add_argument('--csv', '-c', metavar='CSV', dest="in_fhand",
                        type=argparse.FileType('r'),
                        help='CSV with data about photos')
    parser.add_argument('--outdir', '-o', metavar='fpath', dest="out_dir",
                        type=str,
                        help='Output dir')
    parser.add_argument('--plant_part', '-p', metavar='part', dest="plant_part",
                        type=str, help="Part of the plant")
    args = parser.parse_args()
    return args


def main():
    args = define_arguments()
    if not os.path.exists(args.out_dir):
        os.mkdir(args.out_dir)

    for entry in csv.DictReader(args.in_fhand, delimiter=','):
        fpath = entry['fpath']
        plant_info = {"plant_id": entry['plant_id'],
                      "img_id": entry['image_id'],
                      "assay": entry['assay'],
                      "project": entry['project'],
                      "plant_part": args.plant_part}
        out_fpath = _copy_file(fpath, args.out_dir, plant_info)
        add_json_metadata(plant_info, out_fpath)

if __name__ == '__main__':
    main()
