import json
import warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from gi.repository import GExiv2


def add_json_metadata(metadata, fpath):
    exif = GExiv2.Metadata(fpath)
    json_metadata = json.dumps(metadata, sort_keys=True)
    exif["Exif.Photo.UserComment"] = json_metadata
    exif.save_file()


def get_exif_metadata(fpath):
    exif = GExiv2.Metadata(fpath)
    return exif


def get_exif_comments(fpath):
    exif = get_exif_metadata(fpath)
    exif_comments = exif["Exif.Photo.UserComment"]
    try:
        metadata = json.loads(exif_comments)
    except json.decoder.JSONDecodeError:
        raise
    if "image_id" not in metadata:
        msg = "Image doesn't have an Image_ID: {}"
        raise ValueError(msg)
    return metadata
