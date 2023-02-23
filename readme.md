# Storm Tiler

Software to generate map tiles for Storm Platform from the source weather models. Uses ECMWF Magics library to render maps

### Installation

System components:

#### Magics:

`apt-get install magics++`

On Ubuntu systems you may have problems with files location. Magics
will be installed in

`/usr/share/magics`

But python wrappers will expect it in 

`/lib/share/magics`

It may be fixed by symbolic links

#### WRF-Python: 

requires fortran compiler:

`apt-get install gfortran`

#### Python dependencies install:

`python -m pip install -r requirements.txt`

### System Settings

Main settings are read from the system environment

`DATA_SOURCE_DIR=/home/splatform/storm-wrf`

Source NetCDF files are expected in *subfolder* of folder listed here

`NETCDF_BANDS=/home/splatform/storm-nc/{band}/ncfile_{ts}`

Template where to store intermediate per-band NetCDF files. Should include {band} and {ts}

`TILES_DESTINATION=/home/splatform/storm-tiles`

Location where rendered tiles will be stored. You may want to configure also reverse web-proxy like Nginx to use these cached folder bypassing renderer app

`ZOOM_AUTO=5`

Zoom for which tiles are rendered instantly, when data becomes available. Keep it low. Setting it above 5 may cause low performance

`ZOOM_MAX=19`

Maximal allowed zoom for maps. Setting it above 14 have no sense, but not significantly affect performance 

`PORT=5005`

Port which renderer application will bind

### Band Settings

Bans data is in `/bands` folder

Here is example of file:

```
{
    "band": {
        "name": "REFL_10CM",
        "label": "Radar reflectivity",
        "z-priority": 100,
        "layer3d": 0
    },
    "grid_file": {
        "path": "wrtest",
        "file_tpl": "wrfout_d01_{ts}"
    },
    "nc_data": {
        "variable": "refl",
        "units": "dBz",
        "standart_name": "reflectivity"
    },
    "style": "refl.json"
}
```

`band.name` - Internal variable name for this band form source NetCDF file

`band.label` - Band name how it apperas in webapp

`band.z-priority` - Priority of map layer of this band on the webapp map

`band.layer3d` - Index of height layer if using 3D band. Not fill it for 2D bands

`grid_file.path` - Subfolder for source data, inside of DATA_SOURCE_DIR

`grid_file.file_tpl` - Filename template for source models

`nc_data.variable` - Just something meaningful (not used internally)

`nc_data.units` - Just something meaningful (not used internally)

`nc_data.standart_name` - Just something meaningful (not used internally)

`style` - File name with definition of layer Style, used ECMWF Magics definitions