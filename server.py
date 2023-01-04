import random
import os

from renderer import LayerRenderer
from flask import Flask, Response, request, render_template, redirect, url_for, send_file, abort

app = Flask(__name__)


@app.route('/tiles/<band_id>/<layer_id>/<z>/<x>/<y>.png')
def png_tile(band_id, layer_id, z, x, y):

    renderer = LayerRenderer(band_id, layer_id)
    rnd = random.randint(1111111111, 9999999999)
    tmp_path = f"/var/www/puzyrkov.com/storm/tmp/{rnd}"

    renderer.render_tile(
        tmp_path,
        int(z),
        int(x),
        int(y)
    )

    if os.path.exists(tmp_path+".png"):
        return send_file(tmp_path+".png", mimetype='image/png')
    else:
        abort(404)


if __name__ == "__main__":
    app.debug = True
    app.run("0.0.0.0", 5005)
