import unittest
import os
import shutil
import csv
import sys
from tempfile import mkdtemp
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
        csv_fhand = open(csv_fpath)
        plant_entry = list(csv.DictReader(csv_fhand, delimiter=','))[0]

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
            csv_fhand.close()


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


class OrganizeAndAddMetadataTest(unittest.TestCase):

    def test_organize_and_add_bin(self):
        binary = os.path.join(BIN_DIR, 'add_basic_metadata.py')
        csv_fpath = join(TEST_DATA_DIR, 'test.csv')
        out_dir = mkdtemp()
        mypy = sys.executable
        plant_part = 'leaf'
        cmd = [mypy, binary, '-c', csv_fpath, '-o', out_dir, '-p', 'leaf']
        process = Popen(cmd, stderr=PIPE, stdout=PIPE)
        process.communicate()
        assert not process.returncode

        try:
            binary = os.path.join(BIN_DIR, 'add_metadata_and_organize_photos.py')
            out_dir2 = mkdtemp()
            plant_fpath = join(TEST_DATA_DIR, 'NSF1_plants.csv')
            cmd = [sys.executable, binary, '-i', out_dir, '-o', out_dir2,
                   '-p', plant_fpath]
            process = Popen(cmd, stderr=PIPE, stdout=PIPE)
            _, stderr = process.communicate()
            if process.returncode:
                print(stderr)
            assert not process.returncode
            accession = 'BGV007181'

            assert os.listdir(out_dir2) == [accession]
            assert os.listdir(os.path.join(out_dir2, accession)) == [plant_part]
            for image_fname in os.listdir(os.path.join(out_dir2, accession,
                                                       plant_part)):
                if image_fname == 'thumbnails':
                    continue
                image_fpath = os.path.join(out_dir2, accession, plant_part,
                                           image_fname)

                new_metadata = get_metadata(image_fpath)
                assert new_metadata['Accession'] == accession
                assert new_metadata['replica'] == '1'
                assert new_metadata['plant_part'] == plant_part

        finally:
            shutil.rmtree(out_dir)
            shutil.rmtree(out_dir2)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'OrganizeAndAddMetadataTest']
    unittest.main()
