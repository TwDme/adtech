FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y wget build-essential git cmake && \
    apt-get clean

RUN git clone --recursive https://github.com/duckdb/duckdb.git /duckdb

# Build DuckDB
RUN cd /duckdb && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc) && \
    make install


EXPOSE 8000

CMD ["duckdb"]
