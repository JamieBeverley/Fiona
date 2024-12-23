
from fiona.crs import CRS
from fiona.transform import transform_geom
import logging
import os
import random
from datetime import datetime
import psutil
import sys

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)

now = datetime.now().isoformat()
file_handler = logging.FileHandler(
    os.path.join(
        os.path.splitext(os.path.dirname(__file__))[0],
        f"{os.path.basename(__file__)}_{now}.log",
    )
)
logger.addHandler(file_handler)


pid = os.getpid()
process = psutil.Process(pid)
logger.debug(f"Pid: {pid}")


def _get_mock_coordinates(epsg):
    if epsg == 4326:
        longitude = round(random.uniform(-79.57696424675612, -79.26458445595404), 6)
        latitude = round(random.uniform(43.723463973559376, 43.75993665224853), 6)
        return [longitude, latitude]
    elif epsg == 2952:
        return [
            # 0m - 500km
            round(random.uniform(0, 500000), 6),
            # 0m - 5000km
            round(random.uniform(0, 5000000), 6),
        ]
    raise ValueError(f"epsg {epsg} not recognized")


def _geom_generator(epsg, num_rows: int):
    for _ in range(num_rows):
        yield {"type": "Point", "coordinates": _get_mock_coordinates(epsg)}


def log(i, total):
    mem_info = process.memory_full_info()
    memory_usage_mb = mem_info.rss / (1024 * 1024)
    swap_usage_mb = mem_info.swap / (1024 * 1024)
    num_fmt = "{:.10f}"
    logger.debug(
        f"{i}/{total} ({round(i*100/total)}%), "
        f"mem: {num_fmt.format(memory_usage_mb)}MB, "
        f"swap: {num_fmt.format(swap_usage_mb)}MB, "
    )


src_epsg = 4326
dst_epsg = 2952
src_crs = CRS.from_epsg(src_epsg)
dst_crs = CRS.from_epsg(dst_epsg)

log_every = 100
max_rows = 100_000_000

from typing import Iterable
from itertools import islice


def _batched(iterable: Iterable, n: int):
    if n < 1:
        raise ValueError("Batch size must be >= 1")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def test_rowwise():
    for i, geom in enumerate(_geom_generator(src_epsg, num_rows=max_rows)):
        if i % log_every == 0:
            log(i, max_rows)
        transform_geom(src_crs=src_crs, dst_crs=dst_crs, geom=geom)


def test_batched():
    i = 0
    for batch in _batched(_geom_generator(src_epsg, num_rows=max_rows), 5000):
        if i % log_every == 0:
            log(i, max_rows)
        transform_geom(src_crs=src_crs, dst_crs=dst_crs, geom=batch)
        i += len(batch)


start = datetime.now()
logger.info(f"start {start}")

test_rowwise()

end = datetime.now()
logger.info(f"end: {end}")
logger.info(f"duration: {end-start}")