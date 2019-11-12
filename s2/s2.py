from s2sphere import RegionCoverer, LatLng, LatLngRect, CellId, Cell
import json
from shapely.geometry import Polygon, Point

geo_json = json.loads("""
 {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -69.84970092773438,
              -40.90417176411097
            ],
            [
              -70.06668090820312,
              -41.075210270566636
            ],
            [
              -69.49813842773438,
              -41.14556973100949
            ],
            [
              -69.5379638671875,
              -41.269549502842565
            ],
            [
              -69.2083740234375,
              -41.15074024464586
            ],
            [
              -69.40200805664062,
              -40.89898185395097
            ],
            [
              -69.71237182617188,
              -41.019282876045615
            ],
            [
              -69.84970092773438,
              -40.90417176411097
            ]
          ]
        ]
      }
""")

def _geo_json_to_extremes(geo_json):
    
    coordinates = geo_json['coordinates'][0]

    lon = [x[0] for x in coordinates] 
    lat = [x[1] for x in coordinates] 
        
    return lat, lon

def _bbox_polyfill(geo_json, res,):
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
    
    return 'polygon ' + str(geo).replace('], [', ',')\
                        .replace(', ', ' ')\
                        .replace('[', '(')\
                        .replace(']', ')')


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
    """Reverse lookup an S2 address into a geo-coordinate"""
    cell = _token_to_cell(s2_address)
    
    return _to_latlon(LatLng.from_point(cell.get_center()))

def geo_to_s2(lat, lon, res):
    return CellId.from_lat_lng(LatLng.from_degrees(lat, lon)).parent(res)

def s2_get_resolution(s2_address):
    """Returns the resolution of an `h3_address`
    :return: nibble (0-15)
    """
    return _token_to_cell(s2_address).level()

def s2_is_valid(s2_address):
    """Validates an `h3_address`
    :returns: boolean
    """
    try:
        _token_to_cell(s2_address) 
        return True
    except Exception:
        return False

def s2_to_geo_boundary(s2_address, geo_json=False):
    """returns list of coordinates"""
    
    cell = _token_to_cell(s2_address)
    
    return [_to_lonlat(LatLng.from_point(cell.get_vertex(i)))
            for i in [0, 1, 2, 3, 0]] if geo_json else [
            _to_latlon(LatLng.from_point(cell.get_vertex(i)))
            for i in [0, 1, 2, 3]]

def polyfill(geo_json, res, geo_json_conformant=False):
    """        
    :param geo_json_conformant bool: Determines (lat, lng) vs (lng, lat)
        ordering Default is false, which is (lat, lng) ordering, violating
        the spec http://geojson.org/geojson-spec.html#id2 which is (lng, lat)"""
    
    cells = _bbox_polyfill(geo_json, res)
    cells_geo = map(lambda c: s2_to_geo_boundary(c.to_token(), geo_json_conformant), 
                    cells)

    if geo_json_conformant:
        coordinates = geo_json['coordinates'][0]
    else:
        coordinates = list(map(_swipes, geo_json['coordinates'][0]))
        
    return list(filter(
                      lambda c: _geo_intersect(coordinates, c), 
                      cells_geo))