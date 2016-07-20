import unittest
import os
import json
import shutil
import csv
from tempfile import mkdtemp
from os.path import join, dirname, abspath
from subprocess import Popen, PIPE

import imagetools

import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2


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
            exif = GExiv2.Metadata(image_fpath)
            out_plant_info = json.loads(exif["Exif.Photo.UserComment"])

            assert out_plant_info["plant_id"] == plant_entry["plant_id"]
            assert out_plant_info["image_id"] == plant_entry["image_id"]
            assert out_plant_info["plant_part"] == 'leaf'
            assert out_plant_info["assay"] == plant_entry["assay"]
            assert out_plant_info["project"] == plant_entry["project"]

        finally:
            shutil.rmtree(out_dir)


class ScanBinaryTest():
    pass


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
    import sys;sys.argv = ['', 'AddBasicMetadataTest']
    unittest.main()
