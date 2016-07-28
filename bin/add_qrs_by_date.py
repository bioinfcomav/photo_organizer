import os
import csv
import uuid
import argparse

from imagetools.utils import get_all_image_fpaths
from gi.repository import GExiv2


def _get_creation_time(fpath):
    return GExiv2.Metadata(fpath).get_date_time()


def sort_fpaths_by_date(in_dir):
    fpaths = get_all_image_fpaths(in_dir)
    fpaths = sorted(fpaths, key=_get_creation_time)
    return fpaths


def _parse_qr_file(fpath, parent_dir):
    entries = {}
    for entry in csv.DictReader(open(fpath, "r")):
        fpath = os.path.abspath(os.path.join(parent_dir, entry["fpath"]))
        del entry['fpath']
        entries[fpath] = entry
    return entries


def define_arguments():
    parser = argparse.ArgumentParser(description='Scans qrs and return a list')
    parser.add_argument('-i', '--in_dir', required=True,
                        help='Path to the dir with photos to be scanned')
    parser.add_argument('-p', '--project', metavar='project', help='project',
                        required=True)
    parser.add_argument('-a', '--assay', metavar='assay', help='assay',
                        required=True)
    parser.add_argument('-m', '--max', default=20, type=int,
                        metavar='max_photos', help='maximum photos per QR')
    parser.add_argument('-c', '--csv', metavar='csv', help='File path of the generated csv file',
                        required=True)
    args = parser.parse_args()
    return args


def main():
    args = define_arguments()
    in_dir = args.in_dir
    out_qr_fpath = args.csv
    assay = args.assay
    project = args.project
    max_images_by_qr = args.max
    qr_fpath = os.path.join(in_dir, "qr_codes.csv")

    plant_info = None
    # qr_fpath = os.path.join(in_dir, "qr_codes.csv")
    entries = _parse_qr_file(qr_fpath, in_dir)
    out_fhand = open(out_qr_fpath, "w")
    out_fhand.write(open(qr_fpath).readline())
    for fpath in sort_fpaths_by_date(in_dir):
        if fpath in entries:
            by_qr_counter = 0
            plant_info = entries[fpath]
        else:
            if plant_info is None:
                raise RuntimeError('File without previous qr: %s' % (fpath))
            if by_qr_counter > max_images_by_qr:
                msg = 'Too much images for a QR. If you are sure if this is OK, please change max_images_by_qr'
                raise RuntimeError(msg)
            rel_fpath = fpath.replace(in_dir, '.')
            plant_id = plant_info['plant_id']
            image_id = str(uuid.uuid4())
            line = [rel_fpath, plant_id, image_id, project, assay]
            out_fhand.write(','.join(line) + '\n')
            by_qr_counter += 1

if __name__ == '__main__':
    main()
