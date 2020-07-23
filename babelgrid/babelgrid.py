#!/usr/bin/python3
from __future__ import annotations

from typing import List, Tuple, Union, Any, Optional
from collections import namedtuple

from h3 import h3
import shapely
from shapely import wkt
import pyproj
from functools import partial
from shapely.ops import transform

from babelgrid import quadtree, s2

VALID_GRIDS = ["s2", "h3", "bing"]  #'quadtree

RESOLUTION_RANGE = {
    "h3": range(0, 16),
    "s2": range(0, 31),
    "bing": range(1, 24),
    "quadtree": range(1, 24),
}

ShapelyPolys = Union[
    shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon,
]

Point = namedtuple("Point", "latitude longitude")


class Conversors:
    # def __init__(self):
    #     pass

    def any_to_shapely(
        self, polygon: Union[str, dict, ShapelyPolys, List[Any], Tuple[Any],],
    ) -> ShapelyPolys:
        """Convert WKT, geojson to shapely objects.

        Parameters
        ----------
        polygon : Union[str, dict, ShapelyPolys, List[Any], Tuple[Any],]

        Returns
        -------
        ShapelyPolys

        Raises
        ------
        Exception
            If it is not an accepted type.
        """

        if isinstance(
            polygon,
            (
                shapely.geometry.polygon.Polygon,
                shapely.geometry.multipolygon.MultiPolygon,
            ),
        ):

            pass

        elif isinstance(polygon, str):

            polygon = self.from_wkt_to_shapely(polygon)

        elif isinstance(polygon, (list, tuple,)):

            polygon = self.from_list_to_shapely(polygon)

        elif isinstance(polygon, dict):

            polygon = self.from_geojson_to_shapely(polygon)

        else:
            raise Exception(f"{polygon} is not an accepted polygon type")

        return polygon

    @staticmethod
    def from_shapely_to_geojson(polygon: ShapelyPolys) -> dict:

        return shapely.geometry.mapping(polygon)

    @staticmethod
    def from_shapely_to_wkt(polygon: ShapelyPolys) -> str:

        return wkt.dumps(polygon)

    @staticmethod
    def from_wkt_to_shapely(polygon: str) -> ShapelyPolys:

        return wkt.loads(polygon)

    @staticmethod
    def from_geojson_to_shapely(polygon: dict) -> ShapelyPolys:

        return shapely.geometry.shape(polygon)

    @staticmethod
    def from_list_to_shapely(
        polygon: Union[List[Any], Tuple[Any, ...]]
    ) -> shapely.geometry.polygon.Polygon:
        """TODO: Add multipolygon support"""

        return shapely.geometry.Polygon(polygon)


class Polygon(Conversors):
    def __init__(
        self,
        polygon: Union[
            str, dict, shapely.geometry.polygon.Polygon, List[Any], Tuple[Any]
        ],
    ) -> None:

        polygon = self.any_to_shapely(polygon)

        if not isinstance(polygon, shapely.geometry.polygon.Polygon):
            raise Exception(
                f"This is not a shapely.geometry.polygon.Polygon object: {polygon}"
            )

        self.shapely: shapely.geometry.polygon.Polygon = polygon
        self.geojson: dict = self.from_shapely_to_geojson(polygon)
        self.wkt: str = self.from_shapely_to_wkt(polygon)
        self.centroid: Point = Point(
            latitude=polygon.centroid.y, longitude=polygon.centroid.x
        )


class Babel:
    def __init__(self, grid_type: str) -> None:
        """To start the magic, assign a grid_type.

        Parameters
        ----------
        grid_type : str
            Example: 'bing', 'h3', 's2'
        """

        self.grid_type = self._validate_grid(grid_type)

    @staticmethod
    def available_grids() -> List:
        return VALID_GRIDS

    def grid_range(self) -> range:
        return RESOLUTION_RANGE[self.grid_type]

    def _validate_grid(self, grid_type: str):

        if grid_type.lower() not in VALID_GRIDS:
            raise Exception(
                f"{self.grid_type} is not a valid type. "
                "Try one of the following: "
                f'{", ".join(VALID_GRIDS)}'
            )
        else:
            return grid_type.lower()

    def _best_resolution(self, lat: float, area_km: float) -> int:
        """Approximate best resolution given area in km squared.

        TODO: This is not a very efficient method.

        Parameters
        ----------
        lat : float
        area_km : float

        Returns
        -------
        int
            Best resolution
        """

        return min(
            zip(
                self.grid_range(),
                [
                    abs(self.geo_to_tile(lat, 0, resolution).area_km - area_km)
                    for resolution in self.grid_range()
                ],
            ),
            key=lambda t: t[1],
        )[0]

    def _checks_resolution_option(
        self, resolution: Union[int, None], area_km: Union[float, None], latitude: float
    ) -> int:

        if (resolution is None) and (area_km is not None):
            return self._best_resolution(latitude, area_km)

        elif (resolution is None) and (area_km is None):
            raise Exception("Either resolution or area_km has to have a parameter")

        elif (resolution is not None) and (area_km is not None):
            raise Exception("You cannot give a number to both resolution and area_km")

        elif resolution is not None:
            return resolution

    def geo_to_tile(
        self,
        lat: float,
        lon: float,
        resolution: Union[int, None] = None,
        area_km: Union[float, None] = None,
    ) -> Tile:
        """Map coordinate pair (lat, lon) and resolution to a Tile object.

        The Tile object has nice properties. Let's say that `tile` is an
        object from the Tile class.

        ```
        print(tile) --> Tile: grid_type "s2", resolution 14, key 94d28d8b
        tile.geometry.shapely --> to access the shapely object
        tile.geometry.wkt     --> to access the wkt string
        tile.geometry.geojson --> to access the geojson object
        tile.parent           --> to access the tile parent id
        tile.parent           --> to access the tile children id
        ```
        Parameters
        ----------
        lat : float
        lon : float
        resolution : int
            Grid system resolution/zoom/size

        Returns
        -------
        str
            Tile id
        """

        resolution = self._checks_resolution_option(resolution, area_km, lat)

        if self.grid_type == "s2":

            tile_id = s2.geo_to_s2(lat, lon, resolution)

        elif self.grid_type == "h3":

            tile_id = h3.geo_to_h3(lat, lon, resolution)

        elif self.grid_type in ("bing", "quadtree"):

            tile_id = quadtree.geo_to_tile(lat, lon, resolution)

        return self.id_to_tile(tile_id)

    def id_to_tile(self, tile_id: str) -> Tile:
        """Maps tile id to a Tile object.
        
        The Tile object has nice properties. Let's say that `tile` is an
        object from the Tile class.

        ```
        print(tile) --> Tile: grid_type "s2", resolution 14, key 94d28d8b
        tile.geometry.shapely --> to access the shapely object
        tile.geometry.wkt     --> to access the wkt string
        tile.geometry.geojson --> to access the geojson object
        tile.parent           --> to access the tile parent id
        tile.parent           --> to access the tile children id
        ```
        Parameters
        ----------
        tile_id : str

        Returns
        -------
        Tile
        """

        if self.grid_type == "s2":

            return Tile(s2.s2_to_geo_boundary(tile_id, True), tile_id, self.grid_type)

        elif self.grid_type == "h3":

            return Tile(h3.h3_to_geo_boundary(tile_id, True), tile_id, self.grid_type)

        elif self.grid_type in ("bing", "quadtree"):

            return Tile(quadtree.tile_to_geo_boundary(tile_id), tile_id, self.grid_type)

    def polyfill(
        self,
        geometry: Union[
            str,
            dict,
            shapely.geometry.polygon.Polygon,
            shapely.geometry.multipolygon.MultiPolygon,
        ],
        resolution: Union[int, None] = None,
        area_km: Union[float, None] = None,
    ) -> List[Tile]:
        """Fill an arbitrary geometry with tiles of a given resolution or tile area.

        It accepts Polygons or MultiPolygons.

        It returns a list of Tile objects.

        A Tile object has nice properties. Let's say that `tile` is an
        object from the Tile class.

        ```
        print(tile) --> Tile: grid_type "s2", resolution 14, key 94d28d8b
        tile.geometry.shapely --> to access the shapely object
        tile.geometry.wkt     --> to access the wkt string
        tile.geometry.geojson --> to access the geojson object
        tile.parent           --> to access the tile parent id
        tile.parent           --> to access the tile children id
        ```

        You can easily turn it into a geopandas GeoDataFrame

        ```
        gpd.GeoDataFrame([t.to_dict() for t in Babel('h3').polyfill(geometry, resolution=2)])
        ```

        Or plot your result with folium with few lines:

        ```
        import folium

        m = folium.Map()
        for tile in Babel('s2').polyfill(geometry, resolution):
            folium.GeoJson(tile.geometry.geojson).add_to(m)
        m
        ```

        Parameters
        ----------
        geometry : Union[str, dict, shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon]
            Arbitrary geometry. It accepts geojson and wkt, but shapely Objects 
            are prefered.
        resolution : int
            Grid system resolution/zoom/size

        Returns
        -------
        List[Tile]
        """

        flatten = lambda l: [item for sublist in l for item in sublist]

        raw_geometry = Conversors().any_to_shapely(geometry)

        if isinstance(raw_geometry, shapely.geometry.multipolygon.MultiPolygon):
            geometries = [Polygon(g) for g in raw_geometry.geoms]
        elif isinstance(raw_geometry, shapely.geometry.polygon.Polygon):
            geometries = [Polygon(raw_geometry)]

        resolution = self._checks_resolution_option(
            resolution, area_km, raw_geometry.centroid.y
        )

        return flatten([self._polyfill(geom, resolution) for geom in geometries])

    def _polyfill(
        self, geometry: shapely.geometry.polygon.Polygon, resolution: int
    ) -> List[Tile]:
        """Internal polyfill. Calls grids polyfills accordinly.

        Parameters
        ----------
        geometry : shapely.geometry.polygon.Polygon
        resolution : int

        Returns
        -------
        List[Tile]
        """
        if self.grid_type == "s2":

            return [
                Tile(geo["geometry"], geo["id"], "s2")
                for geo in s2.polyfill(geometry.geojson, resolution, True, with_id=True)
            ]

        elif self.grid_type == "h3":

            return [
                Tile(h3.h3_to_geo_boundary(tile_id, True), tile_id, "h3")
                for tile_id in h3.polyfill_geojson(geometry.geojson, resolution)
            ]

        elif self.grid_type in ("bing", "quadtree"):

            return [
                Tile(quadtree.tile_to_geo_boundary(tile_id), tile_id, self.grid_type)
                for tile_id in quadtree.polyfill(geometry.shapely, resolution)
            ]


class Tile(Babel):
    def __init__(
        self,
        polygon: Union[str, dict, shapely.geometry.polygon.Polygon],
        tile_id: str,
        grid_type: str,
    ) -> None:

        self.geometry: Polygon = Polygon(polygon)
        self.tile_id: str = tile_id
        self.grid_type: str = grid_type

    def __str__(self) -> str:

        return self.geometry.wkt

    def __repr__(self) -> str:

        return f'Tile: grid_type "{self.grid_type}", resolution {self.resolution}, tile_id {self.tile_id}'

    def to_dict(self) -> dict:

        return {
            "grid_type": self.grid_type,
            "tile_id": self.tile_id,
            "resolution": self.resolution,
            "parent_id": self.to_parent().tile_id,
            "children_id": [cid.tile_id for cid in self.to_children()],
            "geojson": self.geometry.geojson,
            "wkt": self.geometry.wkt,
            "shapely": self.geometry.shapely,
            "centroid": self.geometry.centroid,
        }

    def to_parent(self) -> Tile:
        """Maps current tile to parent Tile object.

        Returns
        -------
        Tile
        """

        if self.grid_type == "s2":

            parent_id = s2.s2_to_parent(self.tile_id)

        elif self.grid_type == "h3":

            parent_id = h3.h3_to_parent(self.tile_id)

        elif self.grid_type in ("bing", "quadtree"):

            parent_id = quadtree.tile_to_parent(self.tile_id)

        return self.id_to_tile(parent_id)

    def to_children(self) -> List[Tile]:
        """Maps current tile to children Tile objects

        Returns
        -------
        List[Tile]
            List of children Tile objects
        """

        if self.grid_type == "s2":

            children_ids = s2.s2_to_children(self.tile_id)

        elif self.grid_type == "h3":

            children_ids = h3.h3_to_children(self.tile_id)

        elif self.grid_type in ("bing", "quadtree"):

            children_ids = quadtree.tile_to_children(self.tile_id)

        return [self.id_to_tile(cid) for cid in children_ids]

    @property
    def resolution(self) -> int:
        """Maps tile id to resolution/zoom/size

        Parameters
        ----------
        tile_id : str

        Returns
        -------
        int
            Resolution/zoom/size
        """

        if self.grid_type == "s2":

            return s2.s2_get_resolution(self.tile_id)

        elif self.grid_type == "h3":

            return h3.h3_get_resolution(self.tile_id)

        elif self.grid_type in ("bing", "quadtree"):

            return quadtree.tile_get_resolution(self.tile_id)

    @property
    def area_km(self) -> float:
        """Tile area in km squared
        """

        return round(
            transform(
                partial(
                    pyproj.transform,
                    pyproj.Proj("epsg:4326"),
                    pyproj.Proj("epsg:3857"),
                ),
                self.geometry.shapely,
            ).area
            / 10 ** 6,
            10,
        )


if __name__ == "__main__":

    pass
