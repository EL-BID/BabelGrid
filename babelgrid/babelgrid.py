#!/usr/bin/python3
from __future__ import annotations

from typing import List, Tuple, Union

from h3 import h3
import shapely
from shapely import geometry, wkt

from babelgrid.src import quadtree, s2

VALID_GRIDS = ["s2", "h3", "quadtree", "bing"]


class Polygon:
    def __init__(self, polygon: Union[str, dict, shapely.geometry.polygon.Polygon]) -> None:

        if isinstance(polygon, shapely.geometry.polygon.Polygon):

            pass

        elif isinstance(polygon, str):

            polygon = self.from_wkt_to_shapely(polygon)

        elif isinstance(polygon, (list, tuple,)):

            polygon = self.from_list_to_shapely(polygon)

        elif isinstance(polygon, dict):

            polygon = self.from_geojson_to_shapely(polygon)

        self.build_object(polygon)

    def build_object(self, polygon: shapely.geometry.polygon.Polygon) -> None:

        self.shapely: shapely.geometry.polygon.Polygon = polygon
        self.geojson: dict = self.from_shapely_to_geojson(polygon)
        self.wkt: str = self.from_shapely_to_wkt(polygon)

    @staticmethod
    def from_shapely_to_geojson(polygon: shapely.geometry.polygon.Polygon) -> dict:

        return geometry.mapping(polygon)

    @staticmethod
    def from_shapely_to_wkt(polygon: shapely.geometry.polygon.Polygon) -> str:

        return wkt.dumps(polygon)

    @staticmethod
    def from_wkt_to_shapely(polygon: str) -> shapely.geometry.polygon.Polygon:

        return wkt.loads(polygon)

    @staticmethod
    def from_geojson_to_shapely(polygon: dict) -> shapely.geometry.polygon.Polygon:

        return geometry.Polygon(polygon["coordinates"][0])

    @staticmethod
    def from_list_to_shapely(polygon: List) -> shapely.geometry.polygon.Polygon:

        return geometry.Polygon(polygon)


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

    def _validate_grid(self, grid_type: str):

        if grid_type.lower() not in VALID_GRIDS:
            raise Exception(
                f"{self.grid_type} is not a valid type. "
                "Try one of the following: "
                f'{", ".join(VALID_GRIDS)}'
            )
        else:
            return grid_type.lower()

    def geo_to_id(self, lat: float, lon: float, resolution: int) -> str:
        """Map coordinate pair (lat, lon) to tile id.

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

        if self.grid_type == "s2":

            return s2.geo_to_s2(lat, lon, resolution)

        elif self.grid_type == "h3":

            return h3.geo_to_h3(lat, lon, resolution)

        elif self.grid_type in ("bing", "quadtree"):

            return quadtree.geo_to_tile(lat, lon, resolution)

    def id_to_geo_boundary(self, tile_id: str) -> Tile:
        """Maps tile id to geographic boundary Tile object.
        
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

            return Tile(s2.s2_to_geo_boundary(tile_id), tile_id, self.grid_type)

        elif self.grid_type == "h3":

            return Tile(h3.h3_to_geo_boundary(tile_id), tile_id, self.grid_type)

        elif self.grid_type in ("bing", "quadtree"):

            return Tile(quadtree.tile_to_geo_boundary(tile_id), tile_id, self.grid_type)

    def polyfill(
        self, geometry: Union[str, dict, shapely.geometry.polygon.Polygon], resolution: int,
    ) -> List[Tile]:
        """Fill an arbitrary geometry with tiles of a given resolution.

        It returns a list of Tile objects.

        An Tile object has nice properties. Let's say that `tile` is an
        object from the Tile class.

        ```
        print(tile) --> Tile: grid_type "s2", resolution 14, key 94d28d8b
        tile.geometry.shapely --> to access the shapely object
        tile.geometry.wkt     --> to access the wkt string
        tile.geometry.geojson --> to access the geojson object
        tile.parent           --> to access the tile parent id
        tile.parent           --> to access the tile children id
        ```

        You can easily plot your result with folium with few lines:

        ```
        import folium

        m = folium.Map()
        for tile in Babel('s2').polyfill(geometry, resolution):
            folium.GeoJson(tile.geometry.geojson).add_to(m)
        m
        ```

        Parameters
        ----------
        geometry : Union[str, dict, shapely.geometry.polygon.Polygon]
            Arbitrary geometry. It accepts geojson and wkt, but shapely Polygons
            are prefered.
        resolution : int
            Grid system resolution/zoom/size

        Returns
        -------
        List[Tile]
        """

        geometry = Polygon(geometry)

        if self.grid_type == "s2":

            return [
                Tile(geo["geometry"], geo["id"], "s2")
                for geo in s2.polyfill(geometry.geojson, resolution, True, with_id=True)
            ]

        elif self.grid_type == "h3":

            return [
                Tile(h3.h3_to_geo_boundary(tile_id), tile_id, "h3")
                for tile_id in h3.polyfill(geometry.geojson, resolution)
            ]

        elif self.grid_type in ("bing", "quadtree"):

            return [
                Tile(quadtree.tile_to_geo_boundary(tile_id), tile_id, self.grid_type)
                for tile_id in quadtree.polyfill(geometry.shapely, resolution)
            ]

    def id_to_parent(self, tile_id: str) -> str:
        """Maps tile id to parent tile id.

        Parameters
        ----------
        tile_id : str

        Returns
        -------
        str
        """

        if self.grid_type == "s2":

            return s2.s2_to_parent(tile_id)

        elif self.grid_type == "h3":

            return h3.h3_to_parent(tile_id)

        elif self.grid_type in ("bing", "quadtree"):

            return quadtree.tile_to_parent(tile_id)

    def id_to_children(self, tile_id: str) -> List[str]:
        """Maps tile id to children tiles ids

        Parameters
        ----------
        tile_id : str

        Returns
        -------
        List[str]
            List of children tile ids
        """

        if self.grid_type == "s2":

            return s2.s2_to_children(tile_id)

        elif self.grid_type == "h3":

            return h3.h3_to_children(tile_id)

        elif self.grid_type in ("bing", "quadtree"):

            return quadtree.tile_to_children(tile_id)

    def id_get_resolution(self, tile_id: str) -> int:
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

            return s2.s2_get_resolution(tile_id)

        elif self.grid_type == "h3":

            return h3.h3_get_resolution(tile_id)

        elif self.grid_type in ("bing", "quadtree"):

            return quadtree.tile_get_resolution(tile_id)


class Tile(Babel):
    def __init__(
        self,
        polygon: Union[str, dict, shapely.geometry.polygon.Polygon],
        tile_id: str,
        grid_type: str,
    ) -> None:

        self.geometry: Polygon = Polygon(polygon)
        self.centroid: Tuple = (self.geometry.shapely.centroid.x, self.geometry.shapely.centroid.y)
        self.tile_id: str = tile_id
        self.grid_type: str = grid_type
        self.parent_id: str = self.id_to_parent(tile_id)
        self.children_id: str = self.id_to_children(tile_id)
        self.resolution: int = self.id_get_resolution(tile_id)

    def __str__(self) -> str:

        return self.geometry.wkt

    def __repr__(self) -> str:

        return f'Tile: grid_type "{self.grid_type}", resolution {self.resolution}, tile_id {self.tile_id}'

    def to_dict(self) -> dict:

        return {
            "grid_type": self.grid_type,
            "tile_id": self.tile_id,
            "parent_id": self.parent_id,
            "children_id": self.children_id,
            "geojson": self.geometry.geojson,
            "wkt": self.geometry.wkt,
            "shapely": self.geometry.shapely,
            "centroid": self.centroid,
        }


if __name__ == "__main__":

    pass
