#!/usr/bin/env python

import os
import sys
import uuid

from PIL import Image
import zbarlight

IMAGE_MAGIC_NUMBERS = [b'\xFF\xD8\xFF\xE0', b'\xFF\xD8\xFF\xDB',
                       b'\xFF\xD8\xFF\xE1',  # jpg
                       b'\x42\x4D',    # bmp
                       b'\x47\x49\x46\x38\x37\x61',
                       b'\x47\x49\x46\x38\x39\x61',   # gif
                       b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'     # png
                       ]

THRESHOLD_VALUES = [128, 175, 236]


def is_image(fpath):
    if not os.path.isdir(fpath):
        fbegin = open(fpath, 'rb').read(8)
        return any([magic in fbegin for magic in IMAGE_MAGIC_NUMBERS])


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
            for i in THRESHOLD_VALUES:
                image_bw = convert_to_BW(image, i)
                code = zbarlight.scan_codes('qrcode', image_bw)
        if code is None:
            return None
        return code[0]


def main():
    in_dir = sys.argv[1]
    out_fhand = open(sys.argv[2], 'w')
    out_fhand.write('fpath,plant_id,image_id\n')
    for root, dirs, files in os.walk(in_dir, topdown=False):
        for name in files:
            fpath = os.path.join(root, name)
            if is_image(fpath):
                code = _parse_qr(fpath)
                if code is None:
                    code = ''
                out_fhand.write('{},{},{}\n'.format(fpath, code,
                                                    uuid.uuid4()))


def test():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    image1_path = os.path.join(SCRIPT_DIR, 'test_images/IMG_1262.JPG')
    code = _parse_qr(image1_path).decode("utf-8")
    assert code == '0F16NSF1CN02F01M004'
    image1_path = os.path.join(SCRIPT_DIR, 'test_images/1454932909053.jpg')
    assert _parse_qr(image1_path) is None


if __name__ == '__main__':
    test()
    #main()
