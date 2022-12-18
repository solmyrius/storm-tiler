import math
import os

from datetime import datetime, timedelta
from Magics import macro

from coordinates import tile_zxy
from colors import color_schema_reflectivity


class Renderer:

    def __init__(self, tile_folder, src_file, max_zoom, bbox):
        self.tile_folder = tile_folder
        self.src_file = src_file
        self.max_zoom = max_zoom
        self.window = bbox

    def render_tile(self, contours, z, y, x):

        bbox = tile_zxy(z, x, y)
        if not self.in_window(bbox):
            return

        tile_folder = f"{self.tile_folder}/{z}/{x}"
        tile_path = f"{tile_folder}/{y}"
        os.makedirs(tile_folder, exist_ok=True)

        mmap = self.tile_settings(bbox)
        macro_output = self.macro_output(tile_path)
        params_render = {
            'netcdf_filename': self.src_file,
            'netcdf_value_variable': 'refl'
        }

        render_data = []
        render_data.append(macro.mnetcdf(**params_render))
        render_data.append(contours)
        args = [
            macro_output,
            mmap,
        ]
        args += render_data
        macro.plot(*args)

    def in_window(self, bbox):
        in_h = not(bbox[0] > self.window[2] or bbox[2] < self.window[0])
        in_w = not (bbox[1] > self.window[3] or bbox[3] < self.window[1])
        return in_h and in_w

    def render_all(self, contours):
        t1 = datetime.now()
        for z in range(self.max_zoom+1):
            for y in range(int(math.pow(2, z))):
                for x in range(int(math.pow(2, z))):
                    self.render_tile(contours, z, y, x)
        t2 = datetime.now()
        dt = t2-t1
        print(dt.seconds)

    @staticmethod
    def tile_settings(bbox):
        params_mmap = {
            # 'subpage_map_projection': 'EPSG:4326',
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

    @staticmethod
    def contours_style():
        contours = macro.mcont(
            contour="off",
            contour_hilo="off",
            contour_interval=1,
            contour_label="off",
            contour_level_selection_type="interval",
            contour_line_thickness=3,
            contour_shade="on",
            contour_shade_colour_list=color_schema_reflectivity,
            contour_shade_colour_method="list",
            contour_shade_max_level=70,
            contour_shade_method="area_fill",
            contour_shade_min_level=0,
            grib_missing_value_indicator=9999,
            contour_highlight="off"
        )
        return contours

    def run(self):
        contours = self.contours_style()
        self.render_all(contours)
