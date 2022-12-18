"""
Extracts one data band from NetCDF file and creates small .nc file
"""

import os
import netCDF4 as nc


class NCConverter:
    def __init__(self, band, ts, options={}):
        self.band = band
        self.ts = ts
        self.options = {}

        '''Rule for source file name'''
        self.src_path = f"wrfout3/wrfout_d01_{ts}"

        '''Rule for output file name'''
        self.dst_path = f"nc/wrfout_d01_{self.band}_{ts}.nc"

        if "units" in options:
            self.options["units"] = options["units"]
        else:
            self.options["units"] = "Unknown"

        if "standard_name" in options:
            self.options["standard_name"] = options["standard_name"]
        else:
            self.options["standard_name"] = "value"

    def run(self):

        src = nc.Dataset(self.src_path, 'r', format='NETCDF4')

        src_t = src["XTIME"][:]
        src_lon_0 = src["XLONG"][:]
        src_lat_0 = src["XLAT"][:]
        refl_ds = src[self.band][:]

        src_lon = src_lon_0[0][0]

        src_lat = []

        for ll in src_lat_0[0]:
            src_lat.append(ll[0])

        src_refl_0 = refl_ds[0]
        # src_refl = src_refl_0[len(src_refl_0)-1]
        src_refl = src_refl_0[0]

        size_lat = len(src_lat)
        size_lng = len(src_lon)

        dst = nc.Dataset(self.dst_path, 'w', format='NETCDF4')

        dd_lat = dst.createDimension('lat', size_lat)
        dd_lon = dst.createDimension('lon', size_lng)

        dd_lats = dst.createVariable('lat', 'f4', ('lat',))
        dd_lons = dst.createVariable('lon', 'f4', ('lon',))

        value = dst.createVariable('refl', 'f4', ('lat', 'lon',))
        value.units = self.options["units"]
        value.standard_name = self.options["standard_name"]

        dd_lats.standard_name = "latitude"
        dd_lons.standard_name = "longitude"

        dd_lats[:] = src_lat[:]
        dd_lons[:] = src_lon[:]
        value[: , :] = src_refl[:]

        dst.close()
