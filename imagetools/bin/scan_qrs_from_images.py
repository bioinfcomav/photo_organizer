#!/usr/bin/env python

import os
import uuid
import argparse

from PIL import Image
import zbarlight

from imagetools.utils import conf


def is_image(fpath):
    if not os.path.isdir(fpath):
        fbegin = open(fpath, 'rb').read(8)
        return any([magic in fbegin for magic in conf.IMAGE_MAGIC_NUMBERS])


def convert_to_BW(image, threshold):
    gray = image.convert('L')
    bw = gray.point(lambda x: 0 if x < threshold else 255, '1')
    return bw


def _parse_qr(fpath):
    with open(fpath, 'rb') as image_file:
        image = Image.open(image_file)
        image.load()
        code = zbarlight.scan_codes('qrcode', image)
        if code is None:
            for i in conf.THRESHOLD_VALUES:
                image_bw = convert_to_BW(image, i)
                code = zbarlight.scan_codes('qrcode', image_bw)
        if code is None:
            return None
        return str(code[0], "utf-8")


def define_arguments():
    parser = argparse.ArgumentParser(description='Scans qrs and return a list')
    parser.add_argument('--in_dir', '-i', metavar='fpath', dest='in_fpath',
                        type=str, help='FilePath with photos to be scanned')
    parser.add_argument('--out_fhand', '-o', metavar='fpath', dest='out_fhand',
                        type=str, help='FilePath to CSV to be written')
    parser.add_argument('--project', '-p', metavar='project', dest='project',
                        type=str, help='project')
    parser.add_argument('--assay', '-a', metavar='assay', dest='assay',
                        type=str, help='assay')

    args = parser.parse_args()
    return args


def main():
    args = define_arguments()
    out_fhand = open(args.out_fhand, 'w')
    out_fhand.write('fpath,plant_id,image_id,project,assay\n')
    for root, dirs, files in os.walk(args.in_fpath, topdown=False):
        for name in files:
            fpath = os.path.join(root, name)
            if is_image(fpath):
                code = _parse_qr(fpath)
                if code is None:
                    code = ''
                out_fhand.write('{},{},{},{},{}\n'.format(fpath, code,
                                                          uuid.uuid4(),
                                                          args.project,
                                                          args.assay))

if __name__ == '__main__':
    main()
