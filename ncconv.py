"""
Extracts one data band from NetCDF file and creates small .nc file
"""

import os
import netCDF4 as nc


class NCConverter:
    def __init__(
            self,
            band,
            ts,
            src_template,
            dst_template,
            options={}
    ):
        """
        src_template should include {ts} like:
        wrfout3/wrfout_d01_{ts}

        dst_template should include both {ts} and {band} like:
        nc/wrfout_d01_{band}_{ts}.nc
        """
        self.band = band
        self.ts = ts
        self.options = {}

        self.src_path = src_template.format(ts=ts)
        self.dst_path = dst_template.format(ts=ts, band=band)

        if "units" in options:
            self.options["units"] = options["units"]
        else:
            self.options["units"] = "Unknown"

        if "standard_name" in options:
            self.options["standard_name"] = options["standard_name"]
        else:
            self.options["standard_name"] = "value"

        if "variable" in options:
            self.options["variable"] = options["variable"]
        else:
            self.options["variable"] = "variable"

        if "layer3d" in self.options:
            self.options["layer3d"] = self.options["layer3d"]
        else:
            self.options["layer3d"] = None

    def run(self):

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

        dst = nc.Dataset(self.dst_path, 'w', format='NETCDF4')

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
