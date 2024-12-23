
- installing fiona from pypi (`pip install fiona==1.10.1`) results in an
  apperent memory leak/climb on Amazon Linux 2023. On the container:
```bash
pip install fiona==1.10.1
python dev-container/memleak.py
```
and see:
```log
start 2024-12-23 20:49:29.544013
0/100000000 (0%), mem: 44.9882812500MB, swap: 0.0000000000MB, 
... # (this jump is not new/surprising/interesting)
100/100000000 (0%), mem: 49.6171875000MB, swap: 0.0000000000MB, 
... # this jump (and continued climb) is:
21500/100000000 (0%), mem: 49.7421875000MB, swap: 0.0000000000MB, 
...
25700/100000000 (0%), mem: 49.8671875000MB, swap: 0.0000000000MB, 
```

- the issue does not seem to occur when using a locally built/compiled GDAL (?).
  - in `Dockerfile` we build + install GDAL from source
  - then, on the container:
```
pip install -e /fiona
python /fiona/dev-container/memleak.py
```
and see:
```log
100/100000000 (0%), mem: 57.6601562500MB, swap: 0.0000000000MB, 
... # (no climb in mem, stays equivalent...)
113500/100000000 (0%), mem: 57.6601562500MB, swap: 0.0000000000MB, 
```
