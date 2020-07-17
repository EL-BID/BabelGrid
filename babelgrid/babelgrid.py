#!/usr/bin/python3
# code made by [You](https://github.com/@you), YYYY.
from h3 import h3
from s2 import s2

import shapely
from shapely import wkt
from shapely import geometry

VALID_GRIDS = ["s2", "h3"]


class Polygon:
    def __init__(self, polygon):

        if isinstance(polygon, shapely.geometry.polygon.Polygon):

            pass

        elif isinstance(polygon, str):

            polygon = self.from_wkt_to_shapely(polygon)

        elif isinstance(polygon, (list, tuple,)):

            polygon = self.from_list_to_shapely(polygon)

        self.build_object(polygon)

    def build_object(self, polygon):

        self.shapely = polygon
        self.geojson = self.from_shapely_to_geojson(polygon)
        self.wkt = self.from_shapely_to_wkt(polygon)

    def from_shapely_to_geojson(self, polygon):

        return geometry.mapping(polygon)

    def from_shapely_to_wkt(self, polygon):

        return wkt.dumps(polygon)

    def from_wkt_to_shapely(self, polygon):

        return wkt.loads(polygon)

    def from_list_to_shapely(self, polygon):

        return geometry.Polygon(polygon)


class Babel:
    def __init__(self, grid_type):

        self.grid_type = self._validate_grid(grid_type)

    def _validate_grid(self, grid_type):

        if grid_type.lower() not in VALID_GRIDS:
            raise Exception(
                f"{self.grid_type} is not a valid type. "
                "Try one of the following: "
                f'{", ".join(VALID_GRIDS)}'
            )
        else:
            return grid_type.lower()

    def id_to_geo_boundary(self, id):

        if self.grid_type == "s2":

            return Tile(s2.s2_to_geo_boundary(id), id, "s2")

        elif self.grid_type == "h3":

            return Tile(h3.h3_to_geo_boundary(id), id, "h3")

    def polyfill(self, geometry, resolution):

        geometry = Polygon(geometry)

        if self.grid_type == "s2":

            return [
                Tile(geo["geometry"], geo["id"], "s2")
                for geo in s2.polyfill(geometry.geojson, resolution, with_id=True)
            ]

        elif self.grid_type == "h3":

            return [
                Tile(h3.h3_to_geo_boundary(id), id, "h3")
                for id in h3.polyfill(geometry.geojson, resolution)
            ]

    def id_to_parent(self, id):

        if self.grid_type == "s2":

            pass

        elif self.grid_type == "h3":

            return h3.h3_to_parent(id)

    def id_to_children(self, id):

        if self.grid_type == "s2":

            pass

        elif self.grid_type == "h3":

            return h3.h3_to_children(id)

    def id_get_resolution(self, id):

        if self.grid_type == "s2":

            pass

        elif self.grid_type == "h3":

            return h3.h3_get_resolution(id)


class Tile(Babel):

    def __init__(self, polygon, id, grid_type):

        self.geometry = Polygon(polygon)
        self.id = id
        self.grid_type = grid_type
        self.parent_id = self.id_to_parent(id)
        self.children_id = self.id_to_children(id)
        self.resolution = self.id_get_resolution(id)

    def __repr__(self):

        return (
            f"type:{self.grid_type}." f"resolution:{self.resolution}." f"id:{self.id}"
        )

    def to_dict(self):

        return {
            "grid_type": self.grid_type,
            "id": self.id,
            "parent_id": self.parent_id,
            "children_id": self.children_id,
            "geojson": self.geometry.geojson,
            "wkt": self.geometry.wkt,
            "shapely": self.geometry.shapely,
        }


if __name__ == "__main__":

    pass

