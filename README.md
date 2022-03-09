# aiarena-docker-bootstrap

## Prerequisites

Docker needs to be installed in order to use this bootstrap.

## Getting started

### Download or clone this repo
`git clone https://github.com/aiarena/aiarena-docker-bootstrap.git`

### Validating your setup

For windows use the `run.bat` script, for unix use the `run.sh` script.

Before running the script, first check that the MAPS_PATH variable is set correctly for your system.

The script should run a match between the 2 included test bots.

## Running your own matches

1. Bot your bots in the `bots` folder.
2. Add the relevant entries to the `matches` file.
3. Start the run script to run a match.
4. View results in the `results` file and replays in the `replays` folder.
5. For troubleshooting, check the `logs` folder for bot logs or the `client.log` file.

## License

Copyright (c) 2022

Licensed under the [GPLv3 license](LICENSE).
