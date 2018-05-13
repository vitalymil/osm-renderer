FROM ubuntu:16.04
COPY apt.conf /etc/apt/
ENV https_proxy=http://user108:User108!@172.16.0.254:8080
ENV http_proxy=http://user108:User108!@172.16.0.254:8080

RUN apt-get clean
RUN apt-get update

RUN apt-get install -y curl
RUN curl -L https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs

RUN apt-get install -y \
    libboost-all-dev subversion git-core tar unzip \
    wget bzip2 build-essential autoconf libtool libxml2-dev libgeos-dev \
    libgeos++-dev libpq-dev libbz2-dev libproj-dev munin-node munin \
    libprotobuf-c0-dev protobuf-c-compiler libfreetype6-dev libpng12-dev \
    libtiff5-dev libicu-dev libgdal-dev libcairo-dev libcairomm-1.0-dev \
    apache2 apache2-dev libagg-dev liblua5.2-dev ttf-unifont lua5.1 \
    liblua5.1-dev libgeotiff-epsg node-carto gdal-bin libgdal1-dev \
    libmapnik-dev make cmake g++ libboost-dev libboost-system-dev \
    libboost-filesystem-dev libexpat1-dev zlib1g-dev \
    libbz2-dev libpq-dev libproj-dev lua5.2 liblua5.2-dev \
    fonts-noto-cjk fonts-noto-hinted fonts-noto-unhinted ttf-unifont fonts-hanazono \
    python python-pip python3 python3-pip mapnik-utils \
    python-cairo python-setuptools python-cairo-dev

RUN npm i --unsafe-perm -g carto millstone

RUN pip install pyotp overpy fiona

RUN wget https://github.com/googlei18n/noto-fonts/raw/master/hinted/NotoSansArabicUI-Regular.ttf
RUN wget https://github.com/googlei18n/noto-fonts/raw/master/hinted/NotoSansArabicUI-Bold.ttf
RUN mv NotoSansArabicUI-Regular.ttf /usr/share/fonts/truetype/noto/NotoSansArabicUI-Regular.ttf
RUN mv NotoSansArabicUI-Bold.ttf /usr/share/fonts/truetype/noto/NotoSansArabicUI-Bold.ttf

RUN git clone --branch v3.0.16 https://github.com/mapnik/python-mapnik.git
WORKDIR /python-mapnik
RUN PYCAIRO=true python setup.py install
ENV https_proxy=
ENV http_proxy=
