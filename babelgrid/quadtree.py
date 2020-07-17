from pygeotile.tile import Tile
from shapely import wkt


def _centroid_to_key(geometry, resolution):
    return geo_to_tile(geometry.centroid.x, geometry.centroid.y, resolution)


def _key_to_shapely(key):

    return wkt.loads(tile_to_geo_boundary(key))


def _geometry_to_tile_shapely(geometry, resolution):

    return _key_to_shapely(_centroid_to_key(geometry, resolution))


def _get_initial_tile(geometry):

    for initial_resolution in range(1, 1000):
        if not _geometry_to_tile_shapely(geometry, initial_resolution).contains(
            geometry
        ):
            return _centroid_to_key(geometry, initial_resolution - 1)


def _area_ratio(a, b):
    return round(a.intersection(b).area / a.area, 10)


def _get_contained_keys(geometry, initial_key, resolution):

    contained_keys = []

    def func(key, approved):

        if approved:
            if len(key) == resolution:
                contained_keys.append(key)
                return
            else:
                for child_key in tile_to_children(key):
                    func(child_key, True)
        else:
            area_ratio = _area_ratio(_key_to_shapely(key), geometry)

            if area_ratio == 1:
                func(key, True)
            elif area_ratio == 0:
                return
            elif len(key) == resolution:
                contained_keys.append(key)
                return
            else:
                for child_key in tile_to_children(key):
                    func(child_key, False)

    func(initial_key, False)

    return contained_keys


def polyfill(geometry, resolution):

    return _get_contained_keys(geometry, _get_initial_tile(geometry), resolution)


def tile_to_geo_boundary(key):

    a = Tile.from_quad_tree(key)
    return (
        "Polygon (("
        + f"{a.bounds[0].longitude}"
        + " "
        + f"{a.bounds[0].latitude}"
        + ","
        + f"{a.bounds[0].longitude}"
        + " "
        + f"{a.bounds[1].latitude}"
        + ","
        + f"{a.bounds[1].longitude}"
        + " "
        + f"{a.bounds[1].latitude}"
        + ","
        + f"{a.bounds[1].longitude}"
        + " "
        + f"{a.bounds[0].latitude}"
        + ","
        + f"{a.bounds[0].longitude}"
        + " "
        + f"{a.bounds[0].latitude}"
        + "))"
    )


def geo_to_tile(lat, lon, resolution):

    return Tile.for_latitude_longitude(lat, lon, resolution).quad_tree


def tile_get_resolution(key):

    return Tile.from_quad_tree(key).zoom


def tile_to_children(key):

    return tuple([key + str(i) for i in range(4)])


def tile_to_parent(key):

    if len(key) > 1:
        return key[:-1]
    else:
        return key
