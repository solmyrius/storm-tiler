"""
Extracts one data band from NetCDF file and creates small .nc file
"""

import os
import time
import netCDF4 as nc
from styler import Styler


class NCConverter:
    def __init__(self, styler, layer_id):
        self.options = {}
        self.styler = styler
        self.layer_id = layer_id

        self.src_path = styler.get_grid_path(layer_id)
        self.dst_path = styler.get_nc_path(layer_id)
        self.lock_path = styler.get_nc_lock_path(self.layer_id)

        os.makedirs(os.path.dirname(self.dst_path), exist_ok=True)

        band_data = styler.get_band_data()
        nc_data = styler.get_nc_data()

        self.band = band_data["name"]

        if "units" in nc_data:
            self.options["units"] = nc_data["units"]
        else:
            self.options["units"] = "Unknown"

        if "standard_name" in nc_data:
            self.options["standard_name"] = nc_data["standard_name"]
        else:
            self.options["standard_name"] = "value"

        if "variable" in nc_data:
            self.options["variable"] = nc_data["variable"]
        else:
            self.options["variable"] = "variable"

        if "layer3d" in band_data:
            self.options["layer3d"] = band_data["layer3d"]
        else:
            self.options["layer3d"] = None

    def build_band_nc(self):
        src = nc.Dataset(self.src_path, 'r', format='NETCDF4')

        src_t = src["XTIME"][:]
        src_lon_0 = src["XLONG"][:]
        src_lat_0 = src["XLAT"][:]
        band_ds = src[self.band][:]

        src_lon = src_lon_0[0][0]

        src_lat = []

        for ll in src_lat_0[0]:
            src_lat.append(ll[0])

        band_time0 = band_ds[0]

        if self.options["layer3d"] is not None:
            src_band = band_time0[self.options["layer3d"]]
        else:
            src_band = band_time0

        size_lat = len(src_lat)
        size_lng = len(src_lon)

        """
        If file exists it means that it is processed now by the parallel
        thread. We just wait a bit and exit
        """
        try:
            dst = nc.Dataset(self.dst_path, 'w', format='NETCDF4')
        except PermissionError:
            time.sleep(1)
            print("Parallel processing wait/exit")
            return

        dd_lat = dst.createDimension('lat', size_lat)
        dd_lon = dst.createDimension('lon', size_lng)

        dd_lats = dst.createVariable('lat', 'f4', ('lat',))
        dd_lons = dst.createVariable('lon', 'f4', ('lon',))

        value = dst.createVariable(self.options["variable"], 'f4', ('lat', 'lon',))
        value.units = self.options["units"]
        value.standard_name = self.options["standard_name"]

        dd_lats.standard_name = "latitude"
        dd_lons.standard_name = "longitude"

        dd_lats[:] = src_lat[:]
        dd_lons[:] = src_lon[:]
        value[: , :] = src_band[:]

        if self.band == "T2":
            value[: , :] = value[:] - 273.15

        dst.close()

    def build_with_lock(self):
        f = open(self.lock_path, 'w')
        f.write("1")
        f.close()
        self.build_band_nc()
        os.unlink(self.lock_path)

    def run(self):
        tick = 0
        while os.path.exists(self.lock_path) and tick < 10:
            time.sleep(0.5)
            tick = tick + 1
        if os.path.exists(self.lock_path):
            return 1
        self.build_with_lock()
        return 0
