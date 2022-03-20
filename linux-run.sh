#!/bin/bash
# Use this script on Linux without Docker Compose.

export MAPS_PATH=~/StarCraftII/maps

docker run \
  --mount type=bind,source="$(pwd)/config.py",target=/root/aiarena-client/config.py \
  --mount type=bind,source="$(pwd)",target=/root/aiarena-client/host \
  --mount type=bind,source=${MAPS_PATH},target=/root/StarCraftII/maps \
  -it --rm --name arenaclient aiarena/arenaclient