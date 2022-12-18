"""
band - band name in the source file
time_string - datetime component of filename
units - unit name for databand data
standard_name - layer name. It's important to further styling of the data
"""

import os
from dotenv import load_dotenv

from ncconv import NCConverter
from renderer import Renderer

load_dotenv()

TILES_DESTINATION = os.getenv("TILES_DESTINATION")
TEMP_NC = os.getenv("TEMP_NC", "nc")
assert TILES_DESTINATION


def make_tiles(time_string):
    band = "REFL_10CM"
    conv = NCConverter(band, time_string, {
        'units': 'dBz',
        'standart_name': 'reflectivity'
    })
    conv.run()

    renderer = Renderer(
        tile_folder=f"{TILES_DESTINATION}/{band}/{time_string}",
        src_file=f"{TEMP_NC}/wrfout_d01_{band}_{time_string}.nc",
        max_zoom=8,
        bbox=(48.0, 1.0, 54.0, 8.0)
    )
    renderer.run()


def iterate_73():
    for i in range(73):
        m = (i % 6) * 10
        h = i // 6
        hh = h + 15
        d = hh // 24
        hh = hh % 24
        dd = d + 23

        time_string = f"2022-10-{dd:02d}_{hh:02d}_{m:02d}_00"
        print(time_string)
        make_tiles(time_string)


# make_tiles("2022-10-23_17_30_00")
iterate_73()
