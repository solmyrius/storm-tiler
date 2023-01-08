import json
import os
import re
from dotenv import load_dotenv

load_dotenv()


class Styler:

    def __init__(self, style_name):
        self.style_name = style_name
        self.style = None
        self.contour_style = None

        self.netcdf_bands = os.getenv("NETCDF_BANDS", "")
        self.tiles_destination = os.getenv("TILES_DESTINATION", "")
        self.zoom_auto = int(os.getenv("ZOOM_AUTO", 0))
        self.zoom_max = int(os.getenv("ZOOM_MAX", 0))

        if os.path.exists(f"bands/{style_name}.json"):
            f = open(f"bands/{style_name}.json", "r")
            self.style = json.load(f)

    def get_band_data(self):
        return self.style["band"]

    def get_grid_file(self):
        return self.style["grid_file"]

    def get_nc_data(self):
        return self.style["nc_data"]

    def get_style(self):
        if self.contour_style is None:
            f = open(f"styles/{self.style['style']}", "r")
            self.contour_style = json.load(f)

        return self.contour_style

    '''Path to intermediate cache file created for one band'''
    def get_nc_path(self, layer_id):
        return self.netcdf_bands.format(band=self.style_name, ts=layer_id)+".nc"

    def get_nc_lock_path(self, layer_id):
        return self.netcdf_bands.format(band=self.style_name, ts=layer_id)+".txt"

    '''Path to source model file'''
    def get_grid_path(self, layer_id):
        return os.path.join(
            self.style["grid_file"]["path"],
            self.style["grid_file"]["file_tpl"].format(ts=layer_id)
        )

    def get_tile_path(self, layer_id, z, x, y):
        return os.path.join(
            self.tiles_destination,
            self.style_name,
            layer_id,
            z,
            x
        )

    '''
    List layers with the data accessible. May include layer with not
    yet build .nc file and basic tiles
    '''
    def list_layers(self):
        layers = []
        path = self.style["grid_file"]["path"]
        tpl = self.style["grid_file"]["file_tpl"]
        patten = r"" + tpl.replace('{ts}', '(.*)')
        dir_list = os.listdir(path)
        for fname in dir_list:
            mt = re.search(patten, fname)
            if mt:
                layers.append(mt[1])
        return layers
