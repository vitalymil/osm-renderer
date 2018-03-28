FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y libboost-all-dev subversion git-core tar unzip
RUN apt-get install -y wget bzip2 build-essential autoconf libtool libxml2-dev libgeos-dev
RUN apt-get install -y libgeos++-dev libpq-dev libbz2-dev libproj-dev munin-node munin
RUN apt-get install -y libprotobuf-c0-dev protobuf-c-compiler libfreetype6-dev libpng12-dev
RUN apt-get install -y libtiff5-dev libicu-dev libgdal-dev libcairo-dev libcairomm-1.0-dev
RUN apt-get install -y apache2 apache2-dev libagg-dev liblua5.2-dev ttf-unifont lua5.1
RUN apt-get install -y liblua5.1-dev libgeotiff-epsg node-carto gdal-bin libgdal1-dev
RUN apt-get install -y libmapnik-dev mapnik-utils python-mapnik
RUN apt-get install -y make cmake g++ libboost-dev libboost-system-dev
RUN apt-get install -y libboost-filesystem-dev libexpat1-dev zlib1g-dev
RUN apt-get install -y libbz2-dev libpq-dev libproj-dev lua5.2 liblua5.2-dev npm nodejs-legacy

RUN npm i -g carto

RUN apt-get install -y fonts-noto-cjk fonts-noto-hinted fonts-noto-unhinted ttf-unifont fonts-hanazono

RUN apt-get install -y python python-pip python3 python3-pip
RUN apt-get install -y python-cairo python-setuptools
RUN pip install pyotp

RUN wget https://github.com/googlei18n/noto-fonts/raw/master/hinted/NotoSansArabicUI-Regular.ttf
RUN wget https://github.com/googlei18n/noto-fonts/raw/master/hinted/NotoSansArabicUI-Bold.ttf
RUN mv NotoSansArabicUI-Regular.ttf /usr/share/fonts/truetype/noto/NotoSansArabicUI-Regular.ttf
RUN mv NotoSansArabicUI-Bold.ttf /usr/share/fonts/truetype/noto/NotoSansArabicUI-Bold.ttf
