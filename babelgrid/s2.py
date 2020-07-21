from s2sphere import RegionCoverer, LatLng, LatLngRect, CellId, Cell
from shapely.geometry import Polygon


def _geo_json_to_extremes(geo_json):

    coordinates = geo_json["coordinates"][0]

    lon = [x[0] for x in coordinates]
    lat = [x[1] for x in coordinates]

    return lat, lon


def _bbox_polyfill(
    geo_json, res,
):
    """returns list of S2 ids"""

    lat, lon = _geo_json_to_extremes(geo_json)

    p1 = LatLng.from_degrees(min(lat), min(lon))
    p2 = LatLng.from_degrees(max(lat), max(lon))

    region = LatLngRect.from_point_pair(p1, p2)

    coverer = RegionCoverer()
    coverer.min_level = res
    coverer.max_level = res
    return coverer.get_covering(region)


def _geo_to_wkt(geo, repeat_last=True):
    """returns geo as wkt"""

    if repeat_last:
        geo = geo + [geo[-1]]

    return "polygon " + str(geo).replace("], [", ",").replace(", ", " ").replace(
        "[", "("
    ).replace("]", ")")


def _swipes(x):
    return [x[1], x[0]]


def _geo_intersect(geo_1, geo_2):

    return Polygon(geo_1).intersects(Polygon(geo_2))


def _to_latlon(x):
    return [x.lat().degrees, x.lng().degrees]


def _to_lonlat(x):
    return [x.lng().degrees, x.lat().degrees]


def _token_to_cell(s2_address):
    return Cell(CellId.from_token(s2_address))


def s2_to_geo(s2_address):
    """Get geometry from s2 token
    
    Parameters
    ----------
    s2_address : string
        s2 unique token
    
    Returns
    -------
    list
        Geometry of s2 square
    """
    cell = _token_to_cell(s2_address)

    return _to_latlon(LatLng.from_point(cell.get_center()))


def geo_to_s2(lat, lon, res):
    """Get s2 given a point and resolution 
    
    Parameters
    ----------
    lat : float
        latitude
    lon : float
        longitude
    res : int
        s2 square resolution, from 0 to 30
    
    Returns
    -------
    string
        s2 unique token
    """
    return CellId.from_lat_lng(LatLng.from_degrees(lat, lon)).parent(res).to_token()


def s2_get_resolution(s2_address):
    """Gets resolution from s2 token. Resolution can vary
    from 0 to 30
    
    Parameters
    ----------
    s2_address : string
        Unique s2 token
    
    Returns
    -------
    int
        Resolution
    """
    return _token_to_cell(s2_address).level()


def s2_is_valid(s2_address):
    """Checks if s2 token is valid
    
    Parameters
    ----------
    s2_address : string
        Unique s2 token
    
    Returns
    -------
    bool
    """
    try:
        _token_to_cell(s2_address)
        return True
    except Exception:
        return False


def s2_to_children(s2_address):

    return [
        children.to_token() for children in CellId.from_token(s2_address).children()
    ]


def s2_to_parent(s2_address):
    return CellId.from_token(s2_address).parent().to_token()


def s2_to_geo_boundary(s2_address, geo_json_conformant=False):
    """Boundaries of given s2 square
    
    Parameters
    ----------
    s2_address : string
        Unique s2 token
    geo_json : bool, optional
        If True, output coordinates is geo_json conformant (lng, lat)
        If False, coordinates are (lat, lng), by default False
      
    Returns
    -------
    list
        Geometry of given s2 square
    """

    cell = _token_to_cell(s2_address)

    return (
        [_to_lonlat(LatLng.from_point(cell.get_vertex(i))) for i in [0, 1, 2, 3, 0]]
        if geo_json_conformant
        else [_to_latlon(LatLng.from_point(cell.get_vertex(i))) for i in [0, 1, 2, 3]]
    )


def polyfill(geo_json, res, geo_json_conformant=False, with_id=False):
    """Fill a polygon with s2 squares at given resolution
    
    Parameters
    ----------
    geo_json : dict
        Dictionary from a geojson
    res : int
        s2 square resolution, from 0 to 30
    geo_json_conformant : bool, optional
        If True, output coordinates is geo_json conformant (lng, lat)
        If False, coordinates are (lat, lng), by default False
    with_id: bool, optional
        If True, returns list of geometries
        If False, returns list of dict with cell id and geometry

    Returns
    -------
    list 
        List of geometries of s2 squares or cell id with geometry if with_id is True
    """

    cells = _bbox_polyfill(geo_json, res)

    cells_geo = map(
        lambda c: (c.to_token(), s2_to_geo_boundary(c.to_token(), geo_json_conformant)),
        cells,
    )

    if geo_json_conformant:
        coordinates = geo_json["coordinates"][0]
    else:
        coordinates = list(map(_swipes, geo_json["coordinates"][0]))

    filtered = filter(lambda c: _geo_intersect(coordinates, c[1]), cells_geo)

    if with_id:

        return list(map(lambda x: {"id": x[0], "geometry": x[1]}, filtered))

    else:

        return list(map(lambda x: x[1], filtered))
