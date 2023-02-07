import time
import numpy as np
import xarray as xr
from wrf import getvar
import metpy.calc
from metpy.units import units


def compute_helicity(ncconv):

    value_srh = ncconv.nc_dst.createVariable(
        'srh',
        'f4',
        ncconv.dst_dims
    )
    value_srh.units = "meter ** 2 / second ** 2"

    ua = getvar(ncconv.nc_src, "ua")
    va = getvar(ncconv.nc_src, "va")

    """ Height at mass center h_tet """
    xr_data = xr.open_dataset(ncconv.src_path)
    geopot = (xr_data["PH"] + xr_data["PHB"]) * units('m**2/sec**2')
    h = metpy.calc.geopotential_to_height(geopot)
    h0 = h[0]

    uan = ua.to_numpy()
    van = va.to_numpy()
    hn = h0.to_numpy()

    for i in range(value_srh.shape[0]):
        for j in range(value_srh.shape[1]):
            # Storm relative helicity SRH

            h_col = hn[:, i, j]
            u_col = uan[:, i, j]  # U-wind component
            v_col = van[:, i, j]  # V-wind component

            h_col_s1 = h_col.copy()
            np.roll(h_col_s1, -1)
            h_tet = (h_col[0:-1:] + h_col_s1[0:-1:]) / 2  # Height at mass center

            srh_i = integrate_srh(
                h_tet,
                u_col,
                v_col
            )

            value_srh[i, j] = srh_i["srh"]


def integrate_srh(h, u, v):
    res = {}
    srh = 0
    k = len(h)
    for i in range(k-1):
        if h[i] <= 3000:
            srh = srh + u[i+1]*v[i]-u[i]*v[i+1]
    res["srh"] = srh
    return res
