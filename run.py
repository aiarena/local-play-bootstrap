import os
import re
import subprocess
from collections import defaultdict
from multiprocessing.dummy import Pool as ThreadPool, current_process

bot1 = "basic_bot"
race1 = "T"
type1 = "python"

bot2 = "loser_bot"
race2 = "T"
type2 = "python"

maps_path = "D:/Games/StarCraft II/Maps"
thread_pool_size = 3

map_list = ["2000AtmospheresAIE", "BerlingradAIE", "BlackburnAIE", "CuriousMindsAIE", "GlitteringAshesAIE",
            "HardwireAIE"]
games = 10

stats = defaultdict(int)


def printStats():
    print(f"|{' Bot ':<20}|{' Wins ':<6}|")
    print(f"|{'-' * 20}|{'-' * 6}|")
    for key, value in stats.items():
        print(f"| {key:<18} | {value:<4} |")


def parseStreamOutput(stdout):
    for line in stdout.decode('ascii').split('\n'):
        if "Winner" in line:
            finder = re.search(r'Winner=(\w+)', line)
            return finder.group(1)
    return "None"


def play_game(match):
    try:
        process = current_process()
        name = process.name
        print(f"[{process.name}] {match}")
        if not os.path.exists(name):
            os.makedirs(name)
        file = open(f"{name}/matches", "w")
        file.write(match)
        file.close()
        cwd = os.getcwd()
        command = 'docker run' \
                  f' --mount type=bind,source="{cwd}/config.py",target=/root/aiarena-client/config.py' \
                  f' --mount type=bind,source="{cwd}/bots",target=/root/aiarena-client/host/bots' \
                  f' --mount type=bind,source="{cwd}/{name}",target=/root/aiarena-client/host' \
                  f' --mount type=bind,source="{maps_path}",target=/root/StarCraftII/maps' \
                  ' -i --rm aiarena/arenaclient'
        stdout, stderr = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()
        winner = parseStreamOutput(stderr)
        stats[winner] += 1
        print(f"[{name}] Winner {winner}")
    except Exception as error:
        print("[ERROR] {0}".format(str(error)))


def main():
    pool = ThreadPool(thread_pool_size)
    matches = []

    for x in range(games):
        map_index = x % len(map_list)
        matches.append(f"{bot1},{race1},{type1},{bot2},{race2},{type2},{map_list[map_index]}")

    pool.map(play_game, matches)
    pool.close()
    pool.join()
    print("Final stats:")
    printStats()


if __name__ == "__main__":
    main()
