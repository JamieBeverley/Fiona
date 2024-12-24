#!/bin/bash

FIONA_DR=$(realpath ..)

# docker run \
#   -it \
#   --entrypoint /bin/bash \
#   --mount type=bind,src=$FIONA_DR,dst=/fiona \
#   amazon-linux-2023-fiona:latest \
#   -c "pip install -e /fiona && /bin/bash"


docker run \
  -it \
  --mount type=bind,src=$FIONA_DR,dst=/fiona \
  amazon-linux-2023-fiona:latest \
  /bin/bash
