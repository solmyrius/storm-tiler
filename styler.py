import json
import os


class Styler:

    def __init__(self, style_name):
        self.style_name = style_name
        self.style = None
        self.contour_style = None

        f = open(f"bands/{style_name}.json", "r")
        self.style = json.load(f)

    def get_band(self):
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
