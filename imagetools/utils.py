import os
import shutil
from random import Random

IMAGE_MAGIC_NUMBERS = [b'\xFF\xD8\xFF\xE0', b'\xFF\xD8\xFF\xDB',
                       b'\xFF\xD8\xFF\xE1',  # jpg
                       b'\x42\x4D',  # bmp
                       b'\x47\x49\x46\x38\x37\x61',
                       b'\x47\x49\x46\x38\x39\x61',  # gif
                       b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'  # png
                       ]


class RandomNameSequence:
    """An instance of _RandomNameSequence generates an endless
    sequence of unpredictable strings which can safely be incorporated
    into file names.  Each string is six characters long.  Multiple
    threads can safely use the same instance at the same time.

    _RandomNameSequence is an iterator."""

    characters = "abcdefghijklmnopqrstuvwxyz0123456789"

    @property
    def rng(self):
        cur_pid = os.getpid()
        if cur_pid != getattr(self, '_rng_pid', None):
            self._rng = Random()
            self._rng_pid = cur_pid
        return self._rng

    def __iter__(self):
        return self

    def __next__(self):
        c = self.characters
        choose = self.rng.choice
        letters = [choose(c) for dummy in range(8)]
        return ''.join(letters)

NAMER = RandomNameSequence()


def is_image(fpath):
    if not os.path.isdir(fpath):
        fbegin = open(fpath, 'rb').read(8)
        return any([magic in fbegin for magic in IMAGE_MAGIC_NUMBERS])


def copy_file(fpath, out_dir, plant_info):
    random_code = next(NAMER)
    fname = '{}_{}_{}.jpg'.format(plant_info['plant_id'],
                                  plant_info['plant_part'],
                                  random_code)
    dest_fpath = os.path.join(out_dir, fname)
    shutil.copy2(fpath, dest_fpath)
    return dest_fpath
