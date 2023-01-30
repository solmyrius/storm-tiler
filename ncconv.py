"""
Extracts one data band from NetCDF file and creates small .nc file
"""

import os
import numpy as np
import xarray as xr
import time
import math
import netCDF4 as nc
from wrf import getvar
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

        self.nc_src = None
        self.nc_dst = None

    def var_band(self):
        band_data = self.styler.get_band_data()
        return band_data["name"]

    def layer3d(self):
        band_data = self.styler.get_band_data()
        if "layer3d" in band_data:
            return band_data["layer3d"]
        else:
            return None

    def var_name(self):
        nc_data = self.styler.get_nc_data()
        if "variable" in nc_data:
            return nc_data["variable"]
        else:
            return "variable"

    def var_standart_name(self):
        nc_data = self.styler.get_nc_data()
        if "standard_name" in nc_data:
            return nc_data["standard_name"]
        else:
            return "value"

    def var_units(self):
        nc_data = self.styler.get_nc_data()
        if "units" in nc_data:
            return nc_data["units"]
        else:
            return "Unknown"

    def build_band_nc(self):
        """
        If file exists it means that it is processed now by the parallel
        thread. We just wait a bit and exit
        """
        try:
            self.nc_dst = nc.Dataset(self.dst_path, 'w', format='NETCDF4')
        except PermissionError:
            time.sleep(1)
            print("Parallel processing detected wait/exit")
            return

        self.nc_src = nc.Dataset(self.src_path, 'r', format='NETCDF4')
        band_data = self.styler.get_band_data()

        if "type" in band_data and band_data["type"] == "winds":
            self.copy_dims(
                src_lat="XLAT",
                src_lng="XLONG",
                dst_lat="lat",
                dst_lng="lon"
            )
            self.copy_wrf_winds(
                dst_units=self.var_units(),
                dims=('lat', 'lon',)
            )
            self.nc_dst.close()
        else:
            self.copy_dims(
                src_lat="XLAT",
                src_lng="XLONG",
                dst_lat="lat",
                dst_lng="lon"
            )
            self.copy_databand(
                src_name=self.var_band(),
                dst_name=self.var_name(),
                dst_standartname=self.var_standart_name(),
                dst_units=self.var_units(),
                dims=('lat', 'lon',)
            )
            self.nc_dst.close()

    def copy_dims(self, src_lat, src_lng, dst_lat, dst_lng):

        src_lon_0 = self.nc_src[src_lng][:]
        src_lat_0 = self.nc_src[src_lat][:]

        src_lon = src_lon_0[0][0]

        src_lat = []

        for ll in src_lat_0[0]:
            src_lat.append(ll[0])

        size_lat = len(src_lat)
        size_lng = len(src_lon)

        dd_lat = self.nc_dst.createDimension(dst_lat, size_lat)
        dd_lon = self.nc_dst.createDimension(dst_lng, size_lng)

        dd_lats = self.nc_dst.createVariable(dst_lat, 'f4', (dst_lat,))
        dd_lons = self.nc_dst.createVariable(dst_lng, 'f4', (dst_lng,))

        dd_lats.standard_name = "latitude"
        dd_lons.standard_name = "longitude"

        dd_lats[:] = src_lat[:]
        dd_lons[:] = src_lon[:]

    def copy_databand(self, src_name, dst_name, dst_standartname, dst_units, dims):

        band_ds = self.nc_src[src_name][:]
        band_time0 = band_ds[0]

        layer3d = self.layer3d()
        if layer3d is not None:
            src_band = band_time0[layer3d]
        else:
            src_band = band_time0

        value = self.nc_dst.createVariable(
            dst_name,
            'f4',
            dims
        )
        value.units = dst_units
        value.standard_name = dst_standartname

        value[: , :] = src_band[:]

        band_data = self.styler.get_band_data()

        if "math.add" in band_data:
            value[: , :] = value[:] + band_data["math.add"]

        if "math.mult" in band_data:
            value[: , :] = value[:] * band_data["math.mult"]

    def copy_wrf_winds(self, dst_units, dims):
        ua = getvar(self.nc_src, "ua")
        va = getvar(self.nc_src, "va")

        layer3d = self.layer3d()
        if layer3d is not None:
            src_band_u = ua[layer3d]
            src_band_v = va[layer3d]
        else:
            src_band_u = ua[0]
            src_band_v = va[0]

        value_u = self.nc_dst.createVariable(
            'u',
            'f4',
            dims
        )
        value_u.units = dst_units
        value_u.standard_name = 'wind_u'

        value_v = self.nc_dst.createVariable(
            'v',
            'f4',
            dims
        )
        value_v.units = dst_units
        value_v.standard_name = 'wind_v'

        value_v[: , :] = src_band_v[:]
        value_u[: , :] = src_band_u[:]

        band_data = self.styler.get_band_data()
        if "math.add" in band_data:
            value_v[: , :] = value_v[:] + band_data["math.add"]

        if "math.mult" in band_data:
            value_u[: , :] = value_u[:] * band_data["math.mult"]

        value_abs = self.nc_dst.createVariable(
            'wind',
            'f4',
            dims
        )
        value_abs.units = dst_units
        value_abs.standard_name = 'wind'
        value_abs[: , :] = np.sqrt(value_u[:]**2 + value_v[:]**2)

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
