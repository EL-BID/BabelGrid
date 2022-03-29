[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=EL-BID_BabelGrid&metric=alert_status)](https://sonarcloud.io/dashboard?id=EL-BID_BabelGrid)
[![Downloads](https://pepy.tech/badge/babelgrid)](https://pepy.tech/project/babelgrid)
![analytics image (flat)](https://raw.githubusercontent.com/vitr/google-analytics-beacon/master/static/badge-flat.gif)
![analytics](https://www.google-analytics.com/collect?v=1&cid=555&t=pageview&ec=repo&ea=open&dp=/BabelGrid/readme&dt=&tid=UA-4677001-16)

**BabelGrid is a common python API to work with different established geospatial indexing systems.**


Currently, it supports [H3](https://h3geo.org/), [S2](https://s2geometry.io/) and [Bing](https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system) geospatial indexing systems. 
BabelGrid does not have the intention to replace any of the existing APIs, but
to create a common framework that geo-folks can use to easily switch between grids. Also, 
it generates methods around the tiles that ease the data analysis pipeline with seamlessly integration
with well knonw libraries such as Shapely and GeoPandas.

![](https://github.com/EL-BID/BabelGrid/blob/master/imgs/babelgrid_first.gif)

## Start Using It

Install with
```bash
pip install babelgrid
```

- Get a h3 tile with an area of 1km2 in São Paulo, Brasil.
```python
>>> from babelgrid import Babel

>>> tile = Babel('h3').geo_to_tile(lat=-23, lon=-43, area_km=1)
>>> tile
Tile: grid_type "h3", resolution 8, tile_id 88a8a2b66dfffff
```

- Access the geojson, wkt and shapely descriptions of the tile:
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

-  Fill a geometry with s2 tiles of resolution 10
```python
>>> tiles = Babel('s2').polyfill(geometry, resolution=10)
>>> tiles
[Tile: grid_type "s2", resolution 10, tile_id 94d28d,... ,Tile: grid_type "s2", resolution 10, tile_id 94d28f]
```
- Load a geopandas dataframe with the selected tiles
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
One of the most common uses to geospatial indexing systems is to fill up a geometry. This function receives
a geometry that can be a polygon or multipolygons and returns a list of Tile Objects.

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

### The Tile Object

The Tile Object is a central piece of the package. This is the object that is returned by most of the methods implemented. It is good because it 
has some handy features that speed-up the analysis process.

- Easy access to wkt, geojson and shapely geometries

```python
>>> tile.geometry.wkt
>>> tile.geometry.geojson
>>> tile.geometry.shapely
```

- Child and parent transformation

```python
>>> tile.to_parent()
>>> tile.to_children()
```

- Area in km2 already calculated

```python
>>> tile.area_km
```

- To dictonary export of all properties

```python
>>> tile.to_dict()
```

## Grid Systems



|                        | H3                                     | S2                                                   | BING/QuadTree                                                                                     |
|------------------------|----------------------------------------|------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| Tile Shape             | Hexagonal                              | Square                                               | Square                                                                                            |
| Resolution Range       | 0 - 15                                 | 0 - 30                                               | 1 - 23 (infinite)                                                                                 |
| API Reference          | [h3-py](https://github.com/uber/h3-py) | [s2sphere](https://github.com/sidewalklabs/s2sphere) | [pygeotile](https://github.com/geometalab/pyGeoTile)                                              |
| Original Documentation | [H3](https://h3geo.org/)               | [S2 Geometry](https://s2geometry.io/)                | [Bing Maps Tile System](https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system) |

:star: Kudos to all developer of H3, S2 and Bing/QuadTree systems.

### Resolution Reference Table and Plot


Lookup table with grid resolutions at equator by area in km2. 
Note that the area is written in scientific notation (10^x) and x 
is the index of the table.

| Area (10^x km2) | H3    | S2    | BING/QuadTree   |
|-----------:|:------|:------|:----------------|
|          9 | -     | -     | 1               |
|          8 | -     | 0     | 2               |
|          7 | -     | 1,2   | 3,4             |
|          6 | 0,1   | 3,4   | 5,6             |
|          5 | 2     | 5     | 7               |
|          4 | 3     | 6,7   | 8,9             |
|          3 | 4     | 8     | 10,11           |
|          2 | 5     | 9,10  | 12              |
|          1 | 6,7   | 11,12 | 13,14           |
|          0 | 8     | 13    | 15,16           |
|         -1 | 9     | 14,15 | 17              |
|         -2 | 10    | 16,17 | 18,19           |
|         -3 | 11    | 18    | 20,21           |
|         -4 | 12,13 | 19,20 | 22              |
|         -5 | 14    | 21,22 | 23              |
|         -6 | 15    | 23    | -               |
|         -7 | -     | 24,25 | -               |
|         -8 | -     | 26,27 | -               |
|         -9 | -     | 28    | -               |
|        -10 | -     | 29,30 | -               |


![][area-res]

### Tile Area Distortion by Latitude

Depending on how the tile system is built, the area of the tile varies given the latitude. 
For inter-region comparissons, this behaviour can affect the analysis. 

The figure below shows the tile area distortion by geospatial indexing systems. The distortion is defined as

<a href="https://www.codecogs.com/eqnedit.php?latex=D&space;=&space;A_l&space;/&space;A_e" target="_blank"><img src="https://latex.codecogs.com/gif.latex?D&space;=&space;A_l&space;/&space;A_e" title="D = A_l / A_e" /></a>

where <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;A" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;A" title="A" /></a> is the tile area and <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;l" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;l" title="l" /></a> the area given a latitude and <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;e" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;e" title="e" /></a> the equator area. The figure
shows the mean distortion given all resolutions and the error bar is the standard deviation.

![][area-distortion]

[shapely]: https://github.com/EL-BID/BabelGrid/blob/master/imgs/Screen%20Shot%202020-07-20%20at%2019.47.58.png
[polyfill]: https://github.com/EL-BID/BabelGrid/blob/master/imgs/polyfill.png
[area-res]: https://github.com/EL-BID/BabelGrid/blob/master/imgs/gridtype-area-res.png?raw=true
[area-distortion]: https://github.com/EL-BID/BabelGrid/blob/master/imgs/gridtype-distortion.png

## Contributing

Any contribution is very welcomed. You can contribute in several ways:

- Suggest new geospatial indexing systems
- Raise issues with bugs and problems
- Propose new features or behaviours
- Contribute with code maintenence 

## Developing

Start envorinment with

`make create-env`

Update envorinment with

`make update-env`

Publish to PyPi

```bash
poetry version [patch, minor, major]
make publish
```

## Authors

- Joao Carabetta (joaom at iadb.org)

## License

This work is licensed under AM-331-A3 - see the [LICENSE.md](LICENSE.md) file for details.

