
set MAPS_PATH="C:\Program Files (x86)\StarCraft II\Maps"

docker run^
  --mount type=bind,source="%cd%/config.py",target=/root/aiarena-client/config.py^
  --mount type=bind,source="%cd%",target=/root/aiarena-client/host^
  --mount type=bind,source=%MAPS_PATH%,target=/root/StarCraftII/maps^
  -it --rm --name arenaclient aiarena/arenaclient