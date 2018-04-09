#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import overpy
import fiona
import zipfile
import os
import tempfile
import uuid
from fiona.crs import from_epsg
import cgi
import resource
import shutil
import sys

resource.setrlimit(resource.RLIMIT_CPU,(180,180))
resource.setrlimit(resource.RLIMIT_AS,(4000000000, 4000000000))

# Routine to output HTTP headers
def output_headers(content_type, filename = "", length = 0):
  print "Content-Type: %s" % content_type
  if filename:
    print "Content-Disposition: attachment; filename=\"%s\"" % filename
  if length:
    print "Content-Length: %d" % length
  print ""

# Routine to output the contents of a file
def output_file(file):
  file.seek(0)
  shutil.copyfileobj(file, sys.stdout)

# Routine to get the size of a file
def file_size(file):
  return os.fstat(file.fileno()).st_size

# Routine to report an error
def output_error(message, status = "400 Bad Request"):
  print "Status: %s" % status
  output_headers("text/html")
  print "<html>"
  print "<head>"
  print "<title>Error</title>"
  print "</head>"
  print "<body>"
  print "<h1>Error</h1>"
  print "<p>%s</p>" % message
  print "</body>"
  print "</html>"

form = cgi.FieldStorage()

base_dir = os.path.join(tempfile.gettempdir(), 'osm-shp-export')
if not os.path.exists(base_dir):
    os.makedirs(base_dir)

session_dir = os.path.join(base_dir, str(uuid.uuid4()))
os.makedirs(session_dir)

attributes_type = "str:256"
attributes = ["highway", "building", "natural", "waterway", "amenity", 
    "landuse", "place", "railway", "boundary", "power", "leisure", "man_made",
    "shop", "tourism", "route", "historic", "aeroway", "barrier", "military",
    "geological"]

schema = { "properties": {} }
for attribute in attributes:
    schema["properties"][attribute] = attributes_type

bbox = [float(x) for x in form.getvalue("bbox").split(",")]

api = overpy.Overpass()
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
with fiona.open(os.path.join(session_dir, "points.shp"), 'w',crs=from_epsg(4326),driver='ESRI Shapefile', schema=schema) as output:
    for node in result.nodes:
        geometry = {'type': "Point", 'coordinates':(node.lon, node.lat)}
        prop = {}
        for attribute in attributes:
            prop[attribute] = node.tags.get(attribute, None)
        output.write({'geometry': geometry, 'properties':prop})

line_schema = { "geometry": "LineString", "properties": schema["properties"] }
polygon_schema = { "geometry": "Polygon", "properties": schema["properties"] }
with \
    fiona.open(os.path.join(session_dir, "lines.shp"), 'w', crs=from_epsg(4326), driver='ESRI Shapefile', schema=line_schema) as lines_output, \
    fiona.open(os.path.join(session_dir, "polygons.shp"), 'w', crs=from_epsg(4326), driver='ESRI Shapefile', schema=polygon_schema) as polygons_output:
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

zipf = zipfile.ZipFile(os.path.join(session_dir, 'shapefiles.zip'), 'w', zipfile.ZIP_DEFLATED)
for root, dirs, files in os.walk(session_dir):
    for file in files:
        if file != 'shapefiles.zip':
            zipf.write(os.path.join(root, file), file)
zipf.close()

file = open(os.path.join(session_dir, 'shapefiles.zip'))
output_headers("application/zip", "shapefiles.zip", file_size(file))
output_file(file)
file.close()

shutil.rmtree(session_dir, ignore_errors=True)