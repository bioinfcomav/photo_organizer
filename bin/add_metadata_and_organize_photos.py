#!/usr/bin/env python

import argparse
import csv
import os
import shutil

import imagetools
from imagetools.exif import add_json_metadata, get_exif_comments
from imagetools.thumbnail import suggest_thumbnail_path, make_thumbnail
from imagetools.utils import (is_image, create_organized_image_dir,
                              suggest_image_destiny)


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


def define_arguments():
    parser = argparse.ArgumentParser(description='Arrange basic photos by accession')
    parser.add_argument('-i', '--in_dir',
                        help='FilePath with photos to be arranged')
    parser.add_argument('-o', '--out_dir', help='FilePath for arranged photos')
    parser.add_argument('-p', '--plants', type=argparse.FileType('r'),
                        help='CSV with additional info to insert')

    args = parser.parse_args()
    return args


def main():
    args = define_arguments()
    in_dir = os.path.abspath(args.in_dir)
    out_dir = os.path.abspath(args.out_dir)
    plants_fhand = args.plants

    if not os.path.exists(out_dir):
        os.mkdir(args.out_dir)
    plants = parse_plants(plants_fhand)

    for fname in os.listdir(in_dir):
        fpath = os.path.join(in_dir, fname)
        if is_image(fpath):
            metadata = get_exif_comments(fpath)
            plant_metadata = plants[metadata["plant_id"]]
            plant_metadata.update(metadata)
            plant_metadata['version'] = imagetools.__version__

            image_out_dir = create_organized_image_dir(plant_metadata, out_dir)
            dest_fpath = suggest_image_destiny(plant_metadata, image_out_dir)
            shutil.copy(fpath, dest_fpath)
            add_json_metadata(plant_metadata, dest_fpath)
            thumbnail_fpath = suggest_thumbnail_path(dest_fpath)
            make_thumbnail(dest_fpath, thumbnail_fpath)


if __name__ == '__main__':
    main()
