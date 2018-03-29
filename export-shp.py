import overpy
import fiona
import zipfile
import os

from fiona.crs import from_epsg

attributes_type = "str:256"
attributes = ["highway", "building", "natural", "waterway", "amenity", 
    "landuse", "place", "railway", "boundary", "power", "leisure", "man_made",
    "shop", "tourism", "route", "historic", "aeroway", "barrier", "military",
    "geological"]

schema = { "properties": {} }
for attribute in attributes:
    schema["properties"][attribute] = attributes_type

bbox_form = "7.049381732940675,50.87507419144308,7.0569026470184335,50.8767666704248"
bbox = [float(x) for x in bbox_form.split(",")]

api = overpy.Overpass()
# fetch all ways and nodes
result = api.query("""
(
  node(%s,%s,%s,%s);
  (
    way(%s,%s,%s,%s);
    >;
  )
);
out body;
""" % (bbox[1], bbox[0], bbox[3], bbox[2], bbox[1], bbox[0], bbox[3], bbox[2]))

schema["geometry"] = "Point"
with fiona.open("points.shp", 'w',crs=from_epsg(4326),driver='ESRI Shapefile', schema=schema) as output:
    for node in result.nodes:
        geometry = {'type': "Point", 'coordinates':(node.lon, node.lat)}
        prop = {}
        for attribute in attributes:
            prop[attribute] = node.tags.get(attribute, None)
        output.write({'geometry': geometry, 'properties':prop})

line_schema = { "geometry": "LineString", "properties": schema["properties"] }
polygon_schema = { "geometry": "Polygon", "properties": schema["properties"] }
with \
    fiona.open("lines.shp", 'w', crs=from_epsg(4326), driver='ESRI Shapefile', schema=line_schema) as lines_output, \
    fiona.open("polygons.shp", 'w', crs=from_epsg(4326), driver='ESRI Shapefile', schema=polygon_schema) as polygons_output:
    for way in result.ways:
        prop = {}
        for attribute in attributes:
            prop[attribute] = way.tags.get(attribute, None)
        geometry = {'coordinates':[[(node.lon, node.lat) for node in way.nodes]]}
        if way.nodes[0].id == way.nodes[len(way.nodes) - 1].id:
            geometry["type"] = "Polygon"
            polygons_output.write({'geometry': geometry, 'properties':prop})
        else:
            geometry["coordinates"] = geometry["coordinates"][0]
            geometry["type"] = "LineString"
            lines_output.write({'geometry': geometry, 'properties':prop})
