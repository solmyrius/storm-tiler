import json
import os
import re
import pytz
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class Styler:

    def __init__(self, style_name):
        self.band_id = style_name
        self.style = None
        self.contour_style = None

        self.netcdf_bands = os.getenv("NETCDF_BANDS", "")
        self.tiles_destination = os.getenv("TILES_DESTINATION", "")
        self.data_source_dir = os.getenv("DATA_SOURCE_DIR", "")
        self.zoom_auto = int(os.getenv("ZOOM_AUTO", 0))
        self.zoom_max = int(os.getenv("ZOOM_MAX", 0))

        if os.path.exists(f"bands/{style_name}.json"):
            f = open(f"bands/{style_name}.json", "r")
            self.style = json.load(f)

    @property
    def preparer_batch(self):
        if "type" in self.style["band"] and self.style["band"]["type"] == "helicity":
            return "helicity"
        else:
            return "common"

    def get_band_data(self):
        return self.style["band"]

    def get_band_key(self, key):
        if key in self.style["band"]:
            return self.style["band"][key]
        else:
            return None

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
        if self.preparer_batch == "helicity":
            return self.netcdf_bands.format(band="helicity", ts=layer_id)+".nc"
        else:
            return self.netcdf_bands.format(band=self.band_id, ts=layer_id) + ".nc"

    def get_nc_lock_path(self, layer_id):
        return self.netcdf_bands.format(band=self.band_id, ts=layer_id) + ".txt"

    '''Path to source model file'''
    def get_grid_path(self, layer_id):
        return os.path.join(
            self.data_source_dir,
            self.style["grid_file"]["path"],
            self.style["grid_file"]["file_tpl"].format(ts=layer_id)
        )

    def get_tile_path(self, layer_id, z, x, y):
        return os.path.join(
            self.tiles_destination,
            self.band_id,
            layer_id,
            z,
            x
        )

    def list_layers(self):
        """
        List layers with the data accessible. May include layer with not
        yet build .nc file and basic tiles
        """
        layers = []
        path = os.path.join(
            self.data_source_dir,
            self.style["grid_file"]["path"]
        )
        tpl = self.style["grid_file"]["file_tpl"]
        patten = r"" + tpl.replace('{ts}', '(.*)')
        dir_list = os.listdir(path)
        dir_list.sort()
        for fname in dir_list:
            mt = re.search(patten, fname)
            if mt:
                layers.append(mt[1])
        return layers

    def list_ready_layers(self):
        """
        List layers which are ready to use on frontend side
        """
        layers = []
        layer_times = []
        layer_ids = self.list_layers()
        for layer_id in layer_ids:
            nc_path = self.get_nc_path(layer_id)
            nc_lock_path = self.get_nc_lock_path(layer_id)
            if os.path.exists(nc_path):
                if not os.path.exists(nc_lock_path):
                    layer_time = datetime.strptime(layer_id, "%Y-%m-%d_%H_%M_%S")
                    layers.append({
                        'layer_id': layer_id,
                        'layer_time': layer_time,
                        'label': layer_time.astimezone(pytz.timezone("CET")).strftime("%-d %B %Y %H:%M"),
                        'model_label': "ICON-D2 @1K (15Z)<br />"+layer_time.astimezone(pytz.timezone("CET")).strftime("%Y-%m-%d %H:%M"),
                        'tile_path': 'tiles/' + self.band_id + '/' + layer_id + '/{z}/{x}/{y}.png'
                    })
                    layer_times.append(layer_time)
        last_time = max(layer_times)
        yesterday = last_time - timedelta(days=1)

        layers_selected = []
        for layer in layers:
            if layer["layer_time"] >= yesterday and not (layer["layer_time"].hour == 15 and layer["layer_time"].minute >=0  and layer["layer_time"].minute <=10):
                layers_selected.append(layer)

        return layers_selected
