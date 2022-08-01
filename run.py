import math
import os
import re
import subprocess
import random
import shutil
from loguru import logger
from collections import defaultdict
from distutils.dir_util import copy_tree
from multiprocessing.dummy import Pool as ThreadPool, current_process
bot = ["basic_bot", "Z", "python"]

opponents = [
    ["loser_bot", "T", "python"],
]

maps_path = "D:/Games/StarCraft II/Maps"
thread_pool_size = 2
clean_run = True

map_list = ["2000AtmospheresAIE", "BerlingradAIE", "BlackburnAIE", "CuriousMindsAIE", "GlitteringAshesAIE",
            "HardwireAIE"]
games = len(opponents) * 2

wins = defaultdict(int)
losses = defaultdict(int)
ties = defaultdict(int)


def base_elo(x):
    if x >= 1.0:
        return 999
    if x <= 0.0:
        return -999
    return -400 * math.log10(1 / x - 1)


def erf_inv(x):
    a = 8 * (math.pi - 3) / (3 * math.pi * (4 - math.pi))
    y = math.log(1 - x * x)
    z = 2 / (math.pi * a) + y / 2
    return math.copysign(math.sqrt(math.sqrt(z * z - y / a) - z), x)


def phi_inv(p):
    assert (0 <= p <= 1)
    return math.sqrt(2) * erf_inv(2 * p - 1)


def calculate_elo(wins, losses, ties):
    games = wins + ties + losses
    if games == 0:
        return 0, 0
    score = wins + ties / 2
    score_percent = score / games
    win_percent = wins / games
    loss_percent = losses / games
    tie_percent = ties / games

    win_dev = win_percent * (1 - score_percent) ** 2
    loss_dev = loss_percent * (0 - score_percent) ** 2
    tie_dev = tie_percent * (0.5 - score_percent) ** 2
    stdev = math.sqrt(win_dev + loss_dev + tie_dev) / math.sqrt(games)
    dev_min = score_percent + phi_inv(0.025) * stdev
    dev_max = score_percent + phi_inv(0.975) * stdev
    elo = base_elo(score_percent)
    elo_margin = base_elo(dev_min) - base_elo(dev_max)
    return elo, math.fabs(elo_margin / 2)


def print_stats():
    elos = {}
    elo_margins = {}
    for key, value in wins.items():
        elo, elo_margin = calculate_elo(wins[key], losses[key], ties[key])
        elos[key] = elo
        elo_margins[key] = elo_margin
    elos = dict(sorted(elos.items(), key=lambda x: x[1], reverse=True))
    print(f"|{' Bot ':<30}|{' Elo ':<10}|{' Wins ':<6}|{' Losses ':<8}|{' Ties ':<6}|")
    print(f"|{'-' * 30}|{'-' * 10}|{'-' * 6}|{'-' * 8}|{'-' * 6}|")
    for key, value in elos.items():
        print(
            f"| {key:<28} | {int(round(value)):<4}±{int(round(elo_margins[key])):<3} | {wins[key]:<4} | {losses[key]:<6} | {ties[key]:<4} |")


def parse_stream_output(stdout):
    for line in stdout.decode('ascii').split('\n'):
        if "Winner" in line:
            finder = re.search(r'Winner=(\w+)', line)
            return finder.group(1)
    return None


def play_game(match):
    try:
        process = current_process()
        name = process.name
        logger.info(f"[{process.name}] {match[0][0]}vs{match[1][0]} on {match[2]} starting")
        file = open(f"{name}/matches", "w")
        file.write(f"{match[0][0]},{match[0][1]},{match[0][2]},{match[1][0]},{match[1][1]},{match[1][2]},{match[2]}")
        file.close()
        cwd = os.getcwd()
        command = 'docker run' \
                  ' --memory=4gb' \
                  f' --mount type=bind,source="{cwd}/config.py",target=/root/aiarena-client/config.py' \
                  f' --mount type=bind,source="{cwd}/{name}",target=/root/aiarena-client/host' \
                  f' --mount type=bind,source="{maps_path}",target=/root/StarCraftII/maps' \
                  ' -i --rm aiarena/arenaclient'
        stdout, stderr = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()
        winner = parse_stream_output(stderr)

        if winner and winner != "None":
            wins[winner] += 1
            if winner != match[0][0]:
                losses[match[0][0]] += 1
            else:
                losses[match[1][0]] += 1
        else:
            ties[match[0][0]] += 1
            ties[match[1][0]] += 1
        logger.info(f"[{process.name}] {match[0][0]}vs{match[1][0]} on {match[2]} winner is: {winner}")
    except Exception as error:
        logger.error("[ERROR] {0}".format(str(error)))


def handleRemoveReadonly(func, path, exc):
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def main():
    pool = ThreadPool(thread_pool_size)
    matches = []

    for thread_number in range(thread_pool_size):
        name = f"./Thread-{thread_number+1}"
        if os.path.exists(name) and clean_run:
            shutil.rmtree(name, onerror=handleRemoveReadonly)

        if not os.path.exists(name):
            os.makedirs(name)
            copy_tree(f"./bots/", f"{name}/bots/")

    for x in opponents:
        wins[x[0]] = 0

    maps = None
    for x in range(games):
        if not maps:
            maps = map_list.copy()
            random.shuffle(maps)
        map = maps.pop()
        opponent = opponents[x % len(opponents)]
        matches.append((bot, opponent, map))

    pool.map(play_game, matches)
    pool.close()
    pool.join()
    print("Final stats:")
    print_stats()


if __name__ == "__main__":
    main()
