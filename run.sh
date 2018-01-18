#!/bin/bash

docker rm -f osm-renderer
docker run -d -v $(pwd)/../data/tiles:/var/lib/mod_tile --network osm_network --name osm-renderer -p 2000:80 osm/renderer