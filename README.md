# BabelGrid

**BabelGrid is a common python API to work with different established grid systems.**

Currently, it supports [H3](https://h3geo.org/), [S2](https://s2geometry.io/) and [Bing](https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system) grid systems. 
BabelGrid does not have the intention to replace any of the existing APIs, but
to create a common framework that geo-folks can use to easily switch between grids. Also, 
it generates methods around the tiles that ease the data analysis pipeline with seamlessly integration
with well knonw libraries such as Shapely and GeoPandas.

## Start Using It

Install with
```bash
pip install babelgrid
```

:point_right: Get a h3 tile with an area of 1km2 in São Paulo, Brasil.
```python
>>> from babelgrid import Babel

>>> tile = Babel('h3').geo_to_tile(lat=-23, lon=-43, area_km=1)
>>> tile
Tile: grid_type "h3", resolution 8, tile_id 88a8a2b66dfffff
```

:point_right: Access the geojson, wkt and shapely descriptions of the tile:
```python
>>> tile.geometry.geojson
{'type': 'Polygon',
 'coordinates': (((-42.99741709893686, -23.004282833594505),
   (-42.9932470321478, -23.00127887552568),
   (-42.994161748920796, -22.996608473771282),
   (-42.99924646130203, -22.994942061847414),
   (-43.00341650043048, -22.997946087213307),
   (-43.002501854850166, -23.002616457194414),
   (-42.99741709893686, -23.004282833594505)),)}
>>> tile.geometry.wkt
'POLYGON ((-42.9974170989368574 -23.0042828335945053, -42.9932470321477993 -23.0012788755256814, -42.9941617489207957 -22.9966084737712819, -42.9992464613020289 -22.9949420618474143, -43.0034165004304825 -22.9979460872133075, -43.0025018548501663 -23.0026164571944136, -42.9974170989368574 -23.0042828335945053))'
>>> tile.geometry.shapely
```
![][shapely]

:point_right:     Fill a geometry with s2 tiles of resolution 10
```python
>>> tiles = Babel('s2').polyfill(geometry, resolution=10)
>>> tiles
[Tile: grid_type "s2", resolution 10, tile_id 94d28d,... ,Tile: grid_type "s2", resolution 10, tile_id 94d28f]
```
:point_right: Load a geopandas dataframe with the selected tiles
```python
>>> import geopandas as gpd
>>> gpd.GeoDataFrame([t.to_dict() for t in tiles], geometry='shapely')
```


## Quick Documentation

### Babel

You have to initialize the Babel object with any of the available grids. 

```python
>>> Babel.available_grids()
['s2', 'h3', 'bing']

>>> grid = Babel('s2') # example
```


### geo_to_tile

It receives a coordinate pair (lat, lon) and either the native grid resolution or an area in km2.
If it receives an area, it automatically finds what is the resolution for that tile system and latitute 
that best approximates the given area.

```python
>>> Babel('s2').geo_to_tile(2, 3, resolution=10)
Tile: grid_type "s2", resolution 10, tile_id 100fb1

>>> Babel('bing').geo_to_tile(2, 3, area_km=0.1)
Tile: grid_type "bing", resolution 17, tile_id 12222230201200322

>>> Babel('bing').geo_to_tile(2, 3, area_km=0.1).area_km
0.0934819087
```

### id_to_tile

It receives a tile id and converts it to a Tile Object.

```python
>>> Babel('s2').id_to_tile('100fb1')
Tile: grid_type "s2", resolution 10, tile_id 100fb1
```

### Polyfill
One of the most common uses to grid systems is to fill up a geometry. This function receives
a geometry and returns a list of Tile Objects.

```python
>>> tiles = Babel('s2').polyfill(geometry, resolution=10)
>>> tiles
[Tile: grid_type "s2", resolution 10, tile_id 94d28d,... ,Tile: grid_type "s2", resolution 10, tile_id 94d28f]
```

You can also pass a 'desired' grid area using the parameter `grid_km`.

```python
>>> tiles = Babel('bing').polyfill(geometry, area_km=10)
>>> tiles
[Tile: grid_type "bing", resolution 14, tile_id 21031113121331, ..., Tile: grid_type "bing", resolution 14, tile_id 21031113121333]
```

The image below shows `polyfill` being applied for the same geometry for different grid types and sizes.

![][polyfill]

## Grid Systems


![][area-res]

![][area-distortion]

[shapely]: https://github.com/EL-BID/BabelGrid/blob/master/imgs/Screen%20Shot%202020-07-20%20at%2019.47.58.png
[polyfill]: https://github.com/EL-BID/BabelGrid/blob/master/imgs/polyfill.png
[area-res]: https://github.com/EL-BID/BabelGrid/blob/master/imgs/gridtype-area-res.png?raw=true
[area-distortion]: https://github.com/EL-BID/BabelGrid/blob/master/imgs/gridtype-distortion.png
