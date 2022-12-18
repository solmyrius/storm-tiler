# Storm Tiler

Software to generate map tiles for Storm Platform from the source weather models. Uses ECMWF Magics library to render maps

### Settings

Main settings are read from the system environment

`TILES_DESTINATION`= folder where tile layers for bands will be created

`TEMP_NC`= temporary folder for one-layer .nc files

### Installation

`python -m pip install -r requirements.txt`