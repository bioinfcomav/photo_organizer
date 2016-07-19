
import unittest
import os
from bin import scan_qrs_from_images as scan


class TestScanQrs(unittest.TestCase):

    def test_scan(self):
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        image1_path = os.path.join(SCRIPT_DIR, 'data/images/IMG_1262.JPG')
        image2_path = os.path.join(SCRIPT_DIR, 'data/images/1454932909053.jpg')
        assert scan._parse_qr(image1_path) == '0F16NSF1CN02F01M004'
        assert scan._parse_qr(image2_path) is None
