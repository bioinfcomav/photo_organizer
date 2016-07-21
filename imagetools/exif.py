import json

from gi.repository import GExiv2


def add_json_metadata(metadata, fpath):
    exif = GExiv2.Metadata(fpath)
    json_metadata = json.dumps(metadata, sort_keys=True)
    exif["Exif.Photo.UserComment"] = json_metadata
    exif.save_file()


def get_metadata(fpath):
    exif = GExiv2.Metadata(fpath)
    metadata = json.loads(exif["Exif.Photo.UserComment"])
    if "image_id" not in metadata:
        msg = "Image doesn't have an Image_ID"
        raise ValueError(msg)
    if "plant_id" not in metadata:
        msg = "Image doesn't have an Unique_ID"
        raise ValueError(msg)
    return metadata
