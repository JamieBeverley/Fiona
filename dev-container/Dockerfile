FROM amazonlinux:2023

RUN yum update -y
RUN yum install -y \
    gcc \
    gcc-c++ \
    make \
    wget \
    tar \
    gzip \
    libtool \
    libjpeg-turbo-devel \
    libpng-devel \
    libtiff-devel \
    sqlite-devel \
    libcurl-devel \
    cmake \
    python3 \
    python3-devel \
    python3-pip

# build proj
RUN curl -LO  https://github.com/OSGeo/PROJ/releases/download/9.5.1/proj-9.5.1.tar.gz  && \
  tar -xvf proj-9.5.1.tar.gz  && \
  cd proj-9.5.1  && \
  mkdir build  && \
  cd build  && \
  cmake ..  && \
  cmake --build .   && \
  cmake --build . --target install

# build gdal
RUN curl -LO https://download.osgeo.org/gdal/3.7.0/gdal-3.7.0.tar.gz  && \
    tar -xvf gdal-3.7.0.tar.gz  && \
    cd gdal-3.7.0 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . && \
    cmake --build . --target install

RUN pip install psutil setuptools

ENV LD_LIBRARY_PATH /usr/local/lib64:/usr/local/lib
