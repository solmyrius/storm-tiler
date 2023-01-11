import os

from renderer import LayerRenderer
from flask import Flask, Response, request, render_template, redirect, url_for, send_file, abort, jsonify
from datasource import DataSource

app = Flask(__name__)
ds = DataSource()


@app.route('/tiles/<band_id>/<layer_id>/<z>/<x>/<y>.png')
def png_tile(band_id, layer_id, z, x, y):

    renderer = LayerRenderer(band_id, layer_id)
    if renderer.styler.style is None:
        abort(404)

    tile_path = renderer.styler.get_tile_path(layer_id, str(z), str(x), str(y))
    tile_name = os.path.join(tile_path, str(y))
    os.makedirs(tile_path, exist_ok=True)

    if os.path.exists(tile_name+".png"):
        return send_file(tile_name+".png", mimetype='image/png')

    renderer.render_tile(
        tile_name,
        int(z),
        int(x),
        int(y)
    )

    if os.path.exists(tile_name+".png"):
        return send_file(tile_name+".png", mimetype='image/png')
    else:
        abort(404)


@app.route('/api/weather/layers/<band_id>.json')
def band_layers(band_id):
    return jsonify(ds.list_tile_layers(band_id))


if __name__ == "__main__":
    app.debug = True
    app.run("0.0.0.0", 5005, threaded=True)
