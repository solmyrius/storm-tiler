import math


def tile_zxy(z, x, y):

    # y = math.pow(2, z) - y - 1

    lon1 = (x / math.pow(2, z)) * 360.0 - 180.0
    n1 = math.pi - (2.0 * math.pi * y) / math.pow(2, z)
    lat1 = (180.0 / math.pi) * math.atan(0.5 * (math.exp(n1) - math.exp(-n1)))
    lon2 = ((x + 1) / math.pow(2, z)) * 360.0 - 180.0
    n2 = math.pi - (2.0 * math.pi * (y + 1)) / math.pow(2, z)
    lat2 = (180.0 / math.pi) * math.atan(0.5 * (math.exp(n2) - math.exp(-n2)))

    bbox = (
        lat2,
        lon1,
        lat1,
        lon2
    )
    return bbox
