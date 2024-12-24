
from fiona.crs import CRS
from fiona.transform import transform_geom
import logging
import os
import random
from datetime import datetime
import psutil
import sys
from typing import Iterable
from itertools import islice

SRC_EPSG = 4326
DST_EPSG = 2952
SRC_CRS = CRS.from_epsg(SRC_EPSG)
DST_CRS = CRS.from_epsg(DST_EPSG)

def _get_random_coordinates(epsg):
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
        yield {"type": "Point", "coordinates": _get_random_coordinates(epsg)}


def log_memory(ps, logger):
    mem_info = ps.memory_full_info()
    memory_usage_mb = mem_info.rss / (1024 * 1024)
    swap_usage_mb = mem_info.swap / (1024 * 1024)
    num_fmt = "{:.10f}"
    logger.debug(
        f"mem: {num_fmt.format(memory_usage_mb)}MB, "
        f"swap: {num_fmt.format(swap_usage_mb)}MB, "
    )


def _batched(iterable: Iterable, n: int) -> Iterable[Iterable]:
    if n < 1:
        raise ValueError("Batch size must be >= 1")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def test_rowwise(ps, logger, max_rows):
    i = 0
    for geom in _geom_generator(SRC_EPSG, num_rows=max_rows):
        if i >= 1000:
            log_memory(ps, logger)
            i = 0
        transform_geom(src_crs=SRC_CRS, dst_crs=DST_CRS, geom=geom)
        i += 1


def test_batched(ps, logger, max_rows):
    i = 0
    for batch in _batched(_geom_generator(SRC_EPSG, num_rows=max_rows), 250):
        if i>= 1000:
            log_memory(ps, logger)
            i = 0
        transform_geom(src_crs=SRC_CRS, dst_crs=DST_CRS, geom=batch)
        i += len(batch)

if __name__ == "__main__":
    ### Logging ###
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


    ### PS utils ###
    pid = os.getpid()
    process = psutil.Process(pid)
    logger.debug(f"Pid: {pid}")

    ### Profiling ###
    start = datetime.now()
    logger.info(f"start {start}")
    try:
        test_rowwise(process, logger, max_rows = 100_000_000)
        # test_batched(process, logger, max_rows = 100_000_000)
    finally:
        end = datetime.now()
        logger.info(f"end: {end}")
        logger.info(f"duration: {end-start}")
