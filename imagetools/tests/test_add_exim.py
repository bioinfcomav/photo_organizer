import unittest
from tempfile import mkdtemp
import os
import json

from imagetools.utils.utils import add_json_metadata
from imagetools.bin import add_exim as add
from gi.repository import GExiv2


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
        out_fhand = mkdtemp()
        out_fpath = add._copy_file(in_image_fpath, out_fhand, plant_info)
        add_json_metadata(plant_info, out_fpath)
        out_exif = GExiv2.Metadata(out_fpath)
        out_plant_info = json.loads(out_exif["Exif.Photo.UserComment"])
        assert out_plant_info["Accession"] == "test_accession"
        assert out_plant_info["Synonym"] == "test_synonym"
        assert metadata["img_id"] == out_plant_info["img_id"]
