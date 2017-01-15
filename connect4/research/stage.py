# -*- coding: utf-8 -*-

import sys
import itertools

from game_agents.duel import duel


def run_duels(pairs, games_per_duel):
    pairs_len = len(pairs)
    results = {}
    i = 0
    for first, second in pairs:
        i += 1
        sys.stderr.write('\rDuel: %4d/%4d' % (i, pairs_len))
        sys.stderr.flush()
        scoreboard = duel(first, second, games_per_duel)
        results[first] = results.get(first, 0) + scoreboard[1]
        results[second] = results.get(second, 0) + scoreboard[2]
    sys.stderr.write('\n')
    return results


def configs_stats(drivers_percent_won):
    sums = {}
    counts = {}
    mins = {}
    maxes = {}
    for driver_name, percent_won in drivers_percent_won.items():
        config_name, id = driver_name.rsplit('-', 1)
        sums[config_name] = sums.get(config_name, 0) + percent_won
        counts[config_name] = counts.get(config_name, 0) + 1
        if config_name not in mins or percent_won < mins[config_name]['percent_won']:
            mins[config_name] = {'id': id, 'percent_won': percent_won}
        if config_name not in maxes or percent_won > maxes[config_name]['percent_won']:
            maxes[config_name] = {'id': id, 'percent_won': percent_won}
    stats = {}
    for config_name, percent_sum in sums.items():
        stats[config_name] = {
            'mean_percent_won': percent_sum / counts[config_name],
            'min': mins[config_name],
            'max': maxes[config_name]
        }
    return stats


def print_configs_stats(results, duels_per_driver):
    drivers_percent_won = {driver_name: (points / duels_per_driver(driver_name) * 100) for driver_name, points in results.items()}
    stats = sorted(configs_stats(drivers_percent_won).items(), key=lambda x: x[1]['mean_percent_won'], reverse=True)
    for config_name, info in stats:
        print('%50s - %.2f%% (max: %.2f%%, min: %.2f%%)' % (config_name, info['mean_percent_won'],
                                                            info['max']['percent_won'], info['min']['percent_won']))


def all_play_all(drivers_names, games_per_duel=1):
    if drivers_names is not list:
        drivers_names = list(drivers_names)
    pairs = list(filter(lambda pair: pair[0].rsplit('-', 1)[0] != pair[1].rsplit('-', 1)[0],
                        itertools.permutations(drivers_names, 2)))
    results = run_duels(pairs, games_per_duel)
    print_configs_stats(results, lambda d: len(list(filter(lambda p: d in p, pairs))))


def all_with_random(drivers_names, games_per_duel):
    pairs = []
    for driver_name in drivers_names:
        pairs.append([driver_name, 'random'])
        pairs.append(['random', driver_name])
    results = run_duels(pairs, games_per_duel)
    del results['random']
    duels_per_driver = games_per_duel * 2
    print_configs_stats(results, lambda d: duels_per_driver)
