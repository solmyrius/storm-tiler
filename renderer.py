import json
import math
import os

from datetime import datetime, timedelta
from Magics import macro

from coordinates import tile_zxy
from colors import color_schema_reflectivity
from styler import Styler
from ncconv import NCConverter


class LayerRenderer:

    def __init__(self, band_id, layer_id):
        self.band_id = band_id
        self.layer_id = layer_id
        self.styler = Styler(band_id)
        self.window = (48.0, 1.0, 54.0, 8.0)

    def render_tile(self, path, z, x, y):

        bbox = tile_zxy(z, x, y)
        print(bbox, flush=True)
        if not self.in_window(bbox):
            return

        nc_file = self.styler.get_nc_path(self.layer_id)
        if not os.path.exists(nc_file):
            res = self.make_nc()
            if res != 0:
                return
        nc_data = self.styler.get_nc_data()

        mmap = self.tile_settings(bbox)
        macro_output = self.macro_output(path)
        params_render = {
            "netcdf_filename": nc_file,
            "netcdf_value_variable": nc_data["variable"]
        }

        contours = self.contours_style()

        render_data = []
        render_data.append(macro.mnetcdf(**params_render))
        render_data.append(contours)
        args = [
            macro_output,
            mmap,
        ]
        args += render_data
        macro.plot(*args)

    def render_all(self, max_zoom):
        t1 = datetime.now()
        for z in range(max_zoom+1):
            for y in range(int(math.pow(2, z))):
                for x in range(int(math.pow(2, z))):
                    tile_path = self.styler.get_tile_path(
                        self.layer_id,
                        str(z),
                        str(x),
                        str(y)
                    )
                    tile_name = os.path.join(tile_path, str(y))
                    os.makedirs(tile_path, exist_ok=True)
                    self.render_tile(tile_name, z, x, y)
        t2 = datetime.now()
        dt = t2-t1
        print(dt.seconds)

    def make_nc(self):
        ncc = NCConverter(self.styler, self.layer_id)
        return ncc.run()

    def in_window(self, bbox):
        in_h = not(bbox[0] > self.window[2] or bbox[2] < self.window[0])
        in_w = not (bbox[1] > self.window[3] or bbox[3] < self.window[1])
        return in_h and in_w

    @staticmethod
    def tile_settings(bbox):
        params_mmap = {
            'subpage_map_projection': 'EPSG:3857',
            'subpage_lower_left_latitude': bbox[0],
            'subpage_lower_left_longitude': bbox[1],
            'subpage_upper_right_latitude': bbox[2],
            'subpage_upper_right_longitude': bbox[3],
            'subpage_coordinates_system': 'latlon',
            'subpage_frame': 'off',
            'page_x_length': 6.4,
            'page_y_length': 6.4,
            'super_page_x_length': 6.4,
            'super_page_y_length': 6.4,
            'subpage_x_length': 6.4,
            'subpage_y_length': 6.4,
            'subpage_x_position': 0.0,
            'subpage_y_position': 0.0,
            'output_width': 256,
            'page_frame': 'off',
            'skinny_mode': 'on',
            'page_id_line': 'off',
            'subpage_gutter_percentage': 20.0
        }
        return macro.mmap(**params_mmap)

    @staticmethod
    def macro_output(tile_path):
        return macro.output(
            output_formats=['png'],
            output_name_first_page_number="off",
            output_cairo_transparent_background=True,
            output_width=256,
            output_name=tile_path,
        )

    def contours_style(self):
        j = self.styler.get_style()
        contours = macro.mcont(**j)
        return contours
