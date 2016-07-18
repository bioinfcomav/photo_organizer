IMAGE_MAGIC_NUMBERS = [b'\xFF\xD8\xFF\xE0', b'\xFF\xD8\xFF\xDB',
                       b'\xFF\xD8\xFF\xE1',  # jpg
                       b'\x42\x4D',    # bmp
                       b'\x47\x49\x46\x38\x37\x61',
                       b'\x47\x49\x46\x38\x39\x61',   # gif
                       b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'     # png
                       ]

THRESHOLD_VALUES = [128, 175, 236]
