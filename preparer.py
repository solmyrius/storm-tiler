import os

from datasource import DataSource
from ncconv import NCConverter
from renderer import LayerRenderer


class TilePreparer:
    def __init__(self):
        self.ds = DataSource()

    @staticmethod
    def create_nc(styler, layer_id):
        ncc = NCConverter(styler, layer_id)
        ncc.build_with_lock()

    @staticmethod
    def render_auto_levels(band_id, layer_id, zoom_auto):
        renderer = LayerRenderer(band_id, layer_id)
        renderer.render_all(zoom_auto)

    def run(self):
        bands = self.ds.list_bands()
        for band_id in bands:
            styler = bands[band_id]
            layer_ids = styler.list_layers()
            for layer_id in layer_ids:
                nc_file = styler.get_nc_path(layer_id)
                if not os.path.exists(nc_file):
                    self.create_nc(styler, layer_id)
                    self.render_auto_levels(band_id, layer_id, styler.zoom_auto)


tp = TilePreparer()
tp.run()
