import unittest
import os
import json
from tempfile import mkdtemp

from bin import add_basic_metadata as basic
from gi.repository import GExiv2


class TestAddBasicMetadata(unittest.TestCase):

    def test_add_metadata(self):
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        in_image_fpath = os.path.join(SCRIPT_DIR, 'data/images/IMG_1262.JPG')
        exif = GExiv2.Metadata(in_image_fpath)
        assert exif["Exif.Photo.UserComment"] == ""
        plant_info = {"plant_id": "0F16NSF1CN06F01M035",
                      "image_id": "823d3a64-1bed-4840-bbca-9a4b409c7eda",
                      "plant_part": "Leaf", "assay": "NSF1",
                      "project": "NSF"}
        out_dir = mkdtemp()
        out_fpath = basic._copy_file(in_image_fpath, out_dir, plant_info)
        basic.add_json_metadata(plant_info, out_fpath)
        out_exif = GExiv2.Metadata(out_fpath)
        out_plant_info = json.loads(out_exif["Exif.Photo.UserComment"])
        assert out_plant_info["plant_id"] == "0F16NSF1CN06F01M035"
        assert out_plant_info["image_id"] == "823d3a64-1bed-4840-bbca-9a4b409c7eda"
        assert out_plant_info["plant_part"] == "Leaf"
        assert out_plant_info["assay"] == "NSF1"
        assert out_plant_info["project"] == "NSF"
