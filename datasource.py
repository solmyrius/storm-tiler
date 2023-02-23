import os
from styler import Styler
from operator import itemgetter


class DataSource:

    def __init__(self):
        self.bands = {}
        dir_list = os.listdir('bands')
        for fname in dir_list:
            name, ext = os.path.splitext(fname)
            if ext == '.json':
                self.bands[name] = Styler(name)

    def list_bands(self):
        return self.bands

    def list_tile_bands(self):
        bands = []
        for style_id in self.bands:
            style = self.bands[style_id]
            if style.get_band_key("label"):
                z_priority = style.get_band_key("z-priority")
                if z_priority is None:
                    z_priority = 0
                bands.append({
                    "id": style.band_id,
                    "label": style.get_band_key("label"),
                    "layers": style.list_ready_layers(),
                    "z_priority": z_priority
                })

        bands_sorted = sorted(bands, key=itemgetter("z_priority"), reverse=True)
        return bands_sorted

    def list_tile_layers(self, band_id):
        """ List tile layer ready to show """

        if band_id not in self.bands:
            return None

        styler = self.bands[band_id]
        return styler.list_ready_layers()
