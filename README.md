# local-play-bootstrap

## What is this?
This repo intends to be a pain-free method for SC2 AI bot authors to quickly setup and run local bot matches on their system, using the same set of docker images that the [AI Arena ladder](https://aiarena.net) runs on.

## Prerequisites

This bootstrap requires Docker Compose to run.  


If you've installed Docker on Windows or MacOS then Docker Compose is already installed.  
For other systems: [How to install Docker Compose](https://docs.docker.com/compose/install/)

## Getting started

### Download this repo
![Download this repo](img/download.png)

### Validating your setup

A test match between 2 included test bots along with the map AcropolisAIE is preconfigured to run in the `matches` file.

You can run the test match by executing `docker-compose up` in the base folder of this repo.

## Running your own matches

1. Put your bots in the `./bots` folder.
2. Download the [latest ladder maps](https://aiarena.net//wiki/maps/#wiki-toc-current-map-pool) and place them in this repo's local `./maps` folder.  
   See [Use an alternative maps folder location](#use-an-alternative-maps-folder-location) if you want to use a different maps folder.
2. Add the relevant entries for matches you wish to play to the `matches` file.
3. Run `docker compose up` to run the matches.
4. View results in the `results.json` file and replays in the `replays` folder.

### Multi-threaded matches

Refer to [multithread-example.py](./multithread-example.py) for an example of how to run multiple matches in parallel.

Note that there are aspects of bot games that would need more work to be thread safe, 
such as bots which save data to their data folder.

## Troubleshooting

### Tips

All container and bot logs can be found in the `logs` folder.

Docker container output can also be seen after running the `docker compose up` command.  
You can also revisit the container output of previous runs by running `docker compose logs`.

### Specific scenarios

#### Bots connecting to localhost using default `docker compose up` command
If you encounter an error message resembling the following:
```
2023-08-01T20:25:25.407722Z ERROR common/src/api/api_reference/mod.rs:228: ResponseError(ResponseContent { status: 400, api_error_message: ApiErrorMessage { error: "Could not find port for started process" } })
2023-08-01T20:25:25.407869Z ERROR proxy_controller/src/match_scheduler/mod.rs:209: Failed to start bot 1: error in response: status code 400 Bad Request
Error:ApiErrorMessage { error: "Could not find port for started process" }
```

This signifies that one or both of the bots are attempting to connect to the localhost. 
To resolve this issue, consider adjusting the command line arguments on the bot when 
connecting to the ladder server. 
For instance:

`Bot.exe --GamePort 8080 --LadderServer 172.18.0.2 --StartPort 8080 --OpponentId ABCD`

Alternatively if you're unable to fix this or running legacy bots you can utilize the 
provided `docker-compose-host-network.yml` file to run matches with the following command:

`docker compose -f docker-compose-host-network.yml up`

Please be aware that running multiple games concurrently may not function correctly using this approach.

## Use an alternative maps folder location
It can sometimes be handy to have your maps in another location e.g. if you want to use the same maps folder as your StarCraft II installation.  

To do this, update the SC2 Maps Path setting in the docker-compose.yml file to point to your maps folder.

## Contribute
If you notice issues with setup, or have ideas that might help other bot authors, please feel free to contribute via a pull request.

## License

Copyright (c) 2022

Licensed under the [GPLv3 license](LICENSE).
