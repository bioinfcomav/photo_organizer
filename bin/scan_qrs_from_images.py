#!/usr/bin/env python

import os
import uuid
import argparse

from imagetools.utils import is_image
from imagetools.scan import scan_qr


def define_arguments():
    parser = argparse.ArgumentParser(description='Scans qrs and return a list')
    parser.add_argument('-i', '--in_dir',
                        help='Path to the dir with photos to be scanned')
    parser.add_argument('-p', '--project', metavar='project', help='project')
    parser.add_argument('-a', '--assay', metavar='assay', help='assay')

    args = parser.parse_args()
    return args

def _make_path_relative(path, root_dir):
    return path.replace(root_dir, '.')
    

def main():
    args = define_arguments()
    in_dir = args.in_dir
    assay = args.assay
    project = args.project
    out_fhand = open(os.path.join(in_dir, "qr_codes.csv"), "w")
    out_fhand.write('fpath,plant_id,image_id,project,assay\n')
    for root, _, files in os.walk(in_dir, topdown=False):
        for name in files:
            fpath = os.path.join(root, name)
            rel_fpath = _make_path_relative(fpath, in_dir)
            if is_image(fpath):
                code = scan_qr(fpath)
                if code is None:
                    code = ''
                out_fhand.write('{},{},{},{},{}\n'.format(rel_fpath, code,
                                                          uuid.uuid4(),
                                                          project, assay))

if __name__ == '__main__':
    main()
