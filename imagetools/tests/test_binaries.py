import unittest
import os
import json
import shutil
import csv
import sys
from tempfile import mkdtemp, NamedTemporaryFile
from os.path import join, dirname, abspath
from subprocess import Popen, PIPE

import imagetools
from imagetools.exif import get_metadata


BIN_DIR = abspath(join(dirname(imagetools.__file__), '..', 'bin'))
TEST_DATA_DIR = abspath(join(dirname(imagetools.__file__), 'tests', 'data'))


class AddBasicMetadataTest(unittest.TestCase):

    def test_add_metadata(self):
        binary = os.path.join(BIN_DIR, 'add_basic_metadata.py')
        csv_fpath = join(TEST_DATA_DIR, 'test.csv')
        out_dir = mkdtemp()
        mypy = sys.executable
        cmd = [mypy, binary, '-c', csv_fpath, '-o', out_dir, '-p', 'leaf']

        plant_entry = list(csv.DictReader(open(csv_fpath), delimiter=','))[0]

        try:
            process = Popen(cmd, stderr=PIPE, stdout=PIPE)
            process.communicate()
            assert not process.returncode

            image_fpath = os.path.join(out_dir, os.listdir(out_dir)[0])
            out_plant_info = get_metadata(image_fpath)

            assert out_plant_info["plant_id"] == plant_entry["plant_id"]
            assert out_plant_info["image_id"] == plant_entry["image_id"]
            assert out_plant_info["plant_part"] == 'leaf'
            assert out_plant_info["assay"] == plant_entry["assay"]
            assert out_plant_info["project"] == plant_entry["project"]

        finally:
            shutil.rmtree(out_dir)


class ScanBinaryTest(unittest.TestCase):

    def test_scan_binary(self):
        binary = os.path.join(BIN_DIR, 'scan_qrs_from_images.py')
        image_dir = os.path.join(TEST_DATA_DIR, "images")
        project = "NSF"
        assay = "NSF1"
        mypy = sys.executable
        cmd = [mypy, binary, '-i', image_dir, "-p", project, "-a", assay]
        results_fpath = os.path.join(image_dir, "qr_codes.csv")
        try:
            process = Popen(cmd, stderr=PIPE, stdout=PIPE)
            _, stderr = process.communicate()
            if process.returncode:
                print(stderr)
            assert not process.returncode
            results_fhand = open(results_fpath)
            entries = csv.DictReader(results_fhand, delimiter=',')
            for entry in entries:
                if entry['fpath'] == './IMG_1262.JPG':
                    assert entry["plant_id"] == '0F16NSF1CN02F01M004'
                elif entry['fpath'] == '1454932909053.jpg':
                    assert not entry["plant_id"]
                elif entry['fpath'] == 'test_add_exim.jpg':
                    assert entry["plant_id"] == '0F16NSF1CN02F01M011'

        finally:
            if os.path.exists(results_fpath):
                results_fhand.close()
                os.remove(results_fpath)


class TestAddExim(unittest.TestCase):

    def test_add_exim(self):
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        in_image_fpath = os.path.join(SCRIPT_DIR, 'data/images/test_add_exim.jpg')
        metadata = json.loads(GExiv2.Metadata(in_image_fpath)["Exif.Photo.UserComment"])
        assert type(metadata) == dict
        assert "Accesion" not in metadata
        assert "img_id" in metadata
        plant_info = {"plant_id": '0F16NSF1CN02F01M011',
                      "Accession": "test_accession",
                      "Synonym": "test_synonym"}
        plant_info.update(metadata)
        out_dir = mkdtemp()
        out_fpath = add._copy_file(in_image_fpath, out_dir, plant_info)
        add_json_metadata(plant_info, out_fpath)
        out_exif = GExiv2.Metadata(out_fpath)
        out_plant_info = json.loads(out_exif["Exif.Photo.UserComment"])
        assert out_plant_info["Accession"] == "test_accession"
        assert out_plant_info["Synonym"] == "test_synonym"
        assert metadata["img_id"] == out_plant_info["img_id"]


if __name__ == "__main__":
    import sys;sys.argv = ['', 'ScanBinaryTest']
    unittest.main()
