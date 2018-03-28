#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import cairo
import cgi
import Cookie
import mapnik
import os
import pyotp
import resource
import shutil
import signal
import sys
import tempfile

# Limit maximum CPU time
# The Postscript output format can sometimes take hours
resource.setrlimit(resource.RLIMIT_CPU,(180,180))

# Limit memory usage
# Some odd requests can cause extreme memory usage
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

# Create TOTP token validator
#totp = pyotp.TOTP('<%= @totp_key %>', interval = 3600)

# Parse CGI parameters
form = cgi.FieldStorage()

# Import cookies
cookies = Cookie.SimpleCookie(os.environ.get('HTTP_COOKIE'))

# Make sure we have a user agent
if not os.environ.has_key('HTTP_USER_AGENT'):
  os.environ['HTTP_USER_AGENT'] = 'NONE'

# Make sure we have a referer
if not os.environ.has_key('HTTP_REFERER'):
  os.environ['HTTP_REFERER'] = 'NONE'

# Look for TOTP token
if cookies.has_key('_osm_totp_token'):
  token = cookies['_osm_totp_token'].value
else:
  token = None

# Get the load average
cputimes = [float(n) for n in open("/proc/stat").readline().rstrip().split()[1:-1]]
idletime = cputimes[3] / sum(cputimes)

# Process the request
#if not totp.verify(token, valid_window = 1):
  # Abort if the request didn't have a valid TOTP token
  #output_error("Missing or invalid token")
if idletime < 0.2:
  # Abort if the CPU idle time on the machine is too low
  output_error("The server is too busy at the moment. Please wait a few minutes before trying again.", "503 Service Unavailable")
elif not form.has_key("bbox"):
  # No bounding box specified
  output_error("No bounding box specified")
elif not form.has_key("scale"):
  # No scale specified
  output_error("No scale specified")
elif not form.has_key("format"):
  # No format specified
  output_error("No format specified")
else:
  # Create projection object
  prj = mapnik.Projection("+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over");

  # Get the bounds of the area to render
  bbox = [float(x) for x in form.getvalue("bbox").split(",")]

  if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
    # Bogus bounding box
    output_error("Invalid bounding box")
  else:
    # Project the bounds to the map projection
    bbox = mapnik.forward_(mapnik.Box2d(*bbox), prj)

    # Get the style to use
    style = form.getvalue("style", "default")

    # Calculate the size of the final rendered image
    scale = float(form.getvalue("scale"))
    width = int(bbox.width() / scale / 0.00028)
    height = int(bbox.height() / scale / 0.00028)

    # Limit the size of map we are prepared to produce
    if width * height > 4000000:
      # Map is too large (limit is approximately A2 size)
      output_error("Map too large")
    else:
      # Create map
      map = mapnik.Map(width, height)

      # Load map configuration
      mapnik.load_map(map, "/openstreetmap-carto/mapnik.xml")

      # Zoom the map to the bounding box
      map.zoom_to_box(bbox)

      # Fork so that we can handle crashes rendering the map
      pid = os.fork()

      # Render the map
      if pid == 0:
        if form.getvalue("format") == "png":
          image = mapnik.Image(map.width, map.height)
          mapnik.render(map, image)
          png = image.tostring("png")
          output_headers("image/png", "map.png", len(png))
          sys.stdout.write(png)
        elif form.getvalue("format") == "jpeg":
          image = mapnik.Image(map.width, map.height)
          mapnik.render(map, image)
          jpeg = image.tostring("jpeg")
          output_headers("image/jpeg", "map.jpg", len(jpeg))
          sys.stdout.write(jpeg)
        elif form.getvalue("format") == "svg":
          file = tempfile.NamedTemporaryFile(prefix = "export")
          surface = cairo.SVGSurface(file.name, map.width, map.height)
          mapnik.render(map, surface)
          surface.finish()
          output_headers("image/svg+xml", "map.svg", file_size(file))
          output_file(file)
        elif form.getvalue("format") == "pdf":
          file = tempfile.NamedTemporaryFile(prefix = "export")
          surface = cairo.PDFSurface(file.name, map.width, map.height)
          mapnik.render(map, surface)
          surface.finish()
          output_headers("application/pdf", "map.pdf", file_size(file))
          output_file(file)
        elif form.getvalue("format") == "ps":
          file = tempfile.NamedTemporaryFile(prefix = "export")
          surface = cairo.PSSurface(file.name, map.width, map.height)
          mapnik.render(map, surface)
          surface.finish()
          output_headers("application/postscript", "map.ps", file_size(file))
          output_file(file)
        else:
          output_error("Unknown format '%s'" % form.getvalue("format"))
      else:
        pid, status = os.waitpid(pid, 0)
        if status & 0xff == signal.SIGXCPU:
          output_error("CPU time limit exceeded", "509 Resource Limit Exceeded")
        elif status & 0xff == signal.SIGSEGV:
          output_error("Memory limit exceeded", "509 Resource Limit Exceeded")
        elif status != 0:
          output_error("Internal server error", "500 Internal Server Error")
