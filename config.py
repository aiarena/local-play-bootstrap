import os

from arenaclient.match.matches import FileMatchSource

# GENERAL
ARENA_CLIENT_ID = "aiarenaclient_local"
ROUNDS_PER_RUN = 1
RUN_LOCAL = True
CLEANUP_BETWEEN_ROUNDS = False

BASE_DIRECTORY = "/root/aiarena-client/host/"
LOG_FILE = os.path.join(BASE_DIRECTORY, "client.log")
REPLAYS_DIRECTORY = os.path.join(BASE_DIRECTORY, "replays")
BOTS_DIRECTORY = os.path.join(BASE_DIRECTORY, "bots")
BOT_LOGS_DIRECTORY = os.path.join(BASE_DIRECTORY, "logs")

MATCH_SOURCE_CONFIG = FileMatchSource.FileMatchSourceConfig(
    matches_file=os.path.join(BASE_DIRECTORY, "matches"),
    results_file=os.path.join(BASE_DIRECTORY, "results"),
)


# STARCRAFT
SC2_HOME = "/root/StarCraftII/"
SC2_BINARY = os.path.join(SC2_HOME, "Versions/Base75689/SC2_x64")
MAX_GAME_TIME = 60486
MAX_REAL_TIME = 7200  # 2 hours in seconds
