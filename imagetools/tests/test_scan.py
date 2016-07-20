import unittest
import os
from imagetools.tests.test_binaries import TEST_DATA_DIR
from imagetools.scan import scan_qr


class ScanQrTest(unittest.TestCase):
    def test_qrscan(self):
        image1_path = os.path.join(TEST_DATA_DIR, 'images', 'IMG_1262.JPG')
        image2_path = os.path.join(TEST_DATA_DIR, 'images', '1454932909053.jpg')

        assert scan_qr(image1_path) == '0F16NSF1CN02F01M004'
        assert scan_qr(image2_path) is None

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'AddBasicMetadataTest']
    unittest.main()

