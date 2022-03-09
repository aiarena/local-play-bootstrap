# local-play-bootstrap

## What is this?
This repo intends to be a pain-free method for SC2 AI bot authors to quickly setup and verify that the arena client docker works for running local bot matches on their system.  
This system uses the same docker image that the [SC2 AI Arena ladder](https://aiarena.net) runs on.

## Prerequisites

Docker needs to be installed in order to use this bootstrap.

## Getting started

### Download this repo
![Download this repo](img/download.png)

We recommend against cloning this repo unless you intend to contribute changes.

### Validating your setup

For windows you will use the `run.bat` script, for unix use the `run.sh` script.

Before running the script, first:
1. Download the [Sc2 AI Arena 2022 Season 1 maps](https://aiarena.net/wiki/184/plugin/attachments/download/9/) and place them in your system's StarCraft II maps folder.
2. Check that the MAPS_PATH variable within the run script correctly points to your system's StarCraft II maps folder.  

Now you can run the script.
The script should run a match between the 2 included test bots, as dictated by test match listed in the `matches` file.

## Running your own matches

1. Put your bots in the `bots` folder.
2. Add the relevant entries for matches you wish to play to the `matches` file.
3. Start the run script to run a match.
4. View results in the `results` file and replays in the `replays` folder.
5. For troubleshooting, check the `logs` folder for bot logs or the `client.log` file.

## Contribute
If you notice issues with setup, or have ideas that might help other bot authors, please feel free to contribute via a pull request.

## License

Copyright (c) 2022

Licensed under the [GPLv3 license](LICENSE).
