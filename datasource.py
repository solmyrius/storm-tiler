import os
from styler import Styler


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

    ''' List tile layer ready to show '''
    def list_tile_layers(self, band_id):
        layers = []
        if band_id not in self.bands:
            return None

        styler = self.bands[band_id]
        layer_ids = styler.list_layers()
        for layer_id in layer_ids:
            nc_path = styler.get_nc_path(layer_id)
            nc_lock_path = styler.get_nc_lock_path(layer_id)
            if os.path.exists(nc_path):
                if not os.path.exists(nc_lock_path):
                    layers.append({
                        'layer_id': layer_id,
                        'tile_path': 'tiles/'+band_id+'/'+layer_id+'/{z}/{x}/{y}.png'
                    })
        return layers
