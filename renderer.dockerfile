FROM osm/renderer-base

WORKDIR /

# Need to remove proxy config and change url to local Gitlab
RUN git clone https://github.com/openstreetmap/mod_tile.git

WORKDIR /mod_tile
RUN ./autogen.sh
RUN ./configure
RUN make
RUN make install
RUN make install-mod_tile
RUN ldconfig

WORKDIR /

# Need to remove proxy config and change url to local Gitlab
RUN git clone --branch v4.6.0 https://github.com/gravitystorm/openstreetmap-carto.git

WORKDIR /openstreetmap-carto
RUN git checkout tags/v4.6.0
COPY project.mml .
RUN carto project.mml > mapnik.xml

COPY shapefiles data
RUN ./scripts/get-shapefiles.py -n -u

RUN mkdir /var/lib/mod_tile
RUN mkdir /var/run/renderd
RUN mkdir /cgi-bin

COPY renderd.conf /usr/local/etc/
COPY mod_tile.conf /etc/apache2/conf-available/
COPY rend_site.conf /etc/apache2/sites-available/
COPY export.py /cgi-bin/export
COPY export-shp.py /cgi-bin/export-shp

RUN chmod 777 -R /cgi-bin/

RUN a2enmod alias expires headers remoteip rewrite cgi
RUN a2enconf mod_tile
RUN a2dissite 000-default
RUN a2ensite rend_site
CMD service apache2 start && renderd -f -c /usr/local/etc/renderd.conf