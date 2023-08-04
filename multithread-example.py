import os
import random
import shutil
import subprocess
from multiprocessing.dummy import Pool as ThreadPool

from loguru import logger

###################
# RUNNER SETTINGS #
###################

# all the runner files will be inside this path
root_runners_path = f"./runners/"

# if True, delete all the runner files before starting
clean_run = True

# In case you want to use a different docker-compose file
docker_compose_file = "./docker-compose-multithread-example.yml"

# run this many matches at a time
num_runners = 3

#########################
# MATCH GENERATION CODE #
#########################

# This is an example of how to generate matches

bot = ["basic_bot", "T", "python"]
opponents = [
    ["loser_bot", "T", "python"],
    ["loser_bot", "T", "python"],
    ["loser_bot", "T", "python"],
]
map_list = ["BerlingradAIE"]
num_games = len(opponents)


def get_matches_to_play():
    """
    Returns a list of matches to play
    Edit this function to generate matches your preferred way.
    """
    matches = []
    for x in range(num_games):
        # we add 1 to x because we want the runner id to start at 1
        runner_id = x + 1
        map = random.choice(map_list)
        opponent = opponents[x % len(opponents)]
        matches.append((runner_id, bot, opponent, map))
    return matches


########################################################
# Hopefully you shouldn't need to edit below this line #
########################################################

def play_game(match):
    try:
        # prepare the match runner
        runner_id = match[0]
        logger.info(f"[{runner_id}] {match[1][0]}vs{match[2][0]} on {match[3]} starting")
        runner_dir = prepare_runner_dir(runner_id)
        prepare_matches_and_results_files(match, runner_dir)

        # start the match running
        command = f'docker compose -p {runner_id} -f {docker_compose_file} up'
        subprocess.Popen(
            command,
            shell=True,
        ).communicate()

    except Exception as error:
        logger.error("[ERROR] {0}".format(str(error)))


def prepare_matches_and_results_files(match, runner_dir):
    file = open(f"{runner_dir}/matches", "w")
    # match[1][0] and match[2][1] are twice, because we re-use the bot name as the bot id
    file.write(
        f"{match[1][0]},{match[1][0]},{match[1][1]},{match[1][2]},"  # bot1
        f"{match[2][0]},{match[2][0]},{match[2][1]},{match[2][2]},"  # bot2
        f"{match[3]}")  # map
    file.close()

    # touch results.json
    file = open(f"{runner_dir}/results.json", "w")
    file.close()


def handleRemoveReadonly(func, path, exc):
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def prepare_runner_dir(dir_name) -> str:
    runner_dir = f"{root_runners_path}/{dir_name}"
    if not os.path.exists(runner_dir):
        os.makedirs(runner_dir)
    return runner_dir


def prepare_root_dir():
    if os.path.exists(root_runners_path) and clean_run:
        shutil.rmtree(root_runners_path, onerror=handleRemoveReadonly)
    if not os.path.exists(root_runners_path):
        os.makedirs(root_runners_path)


def main():
    pool = ThreadPool(num_runners)

    prepare_root_dir()

    matches = get_matches_to_play()

    pool.map(play_game, matches)
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
