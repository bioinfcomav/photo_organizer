from PIL import Image
import zbarlight

THRESHOLD_VALUES = [128, 175, 236]


def convert_to_BW(image, threshold):
    gray = image.convert('L')
    bw = gray.point(lambda x: 0 if x < threshold else 255, '1')
    return bw


def scan_qr(fpath):
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
        return str(code[0], "utf-8")
