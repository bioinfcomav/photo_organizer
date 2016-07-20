#!/usr/bin/env python

import csv
import os
import argparse
from imagetools.utils.utils import add_json_metadata, copy_file


def define_arguments():
    parser = argparse.ArgumentParser(description='Add basic metadata to images')
    parser.add_argument('-c', '--csv', metavar='CSV', dest="in_fhand",
                        type=argparse.FileType('r'),
                        help='CSV with data about photos')
    parser.add_argument('-o', '--outdir', dest="out_dir",
                        help='Output dir')
    parser.add_argument('-p', '--plant_part', dest="plant_part",
                        help="Part of the plant")
    args = parser.parse_args()
    return args


def main():
    args = define_arguments()
    in_fhand = args.in_fhand
    plant_part = args.plant_part
    out_dir = args.out_dir
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    csv_dir = os.path.dirname(in_fhand.name)
    for entry in csv.DictReader(in_fhand, delimiter=','):
        fpath = os.path.abspath(os.path.join(csv_dir, entry['fpath']))
        plant_info = {"plant_id": entry['plant_id'],
                      "image_id": entry['image_id'],
                      "assay": entry['assay'],
                      "project": entry['project'],
                      "plant_part": plant_part}
        out_fpath = copy_file(fpath, out_dir, plant_info)
        add_json_metadata(plant_info, out_fpath)

if __name__ == '__main__':
    main()
