import cProfile

from game_agents.reinforcement_backend.reinforcementplayer import ReinforcementPlayer
from storages.neuralstorage import NeuralStorage

config = {
    "board": {
        "cols": 7,
        "rows": 6
    },
    "needed_to_win": 4,
    "neural_store": {
        "file_name": "storages/stored_data/reinforcement/first.xml",
        "hidden_neurons": 50
    },
    "rewards": {
        "each_move": -0.01,
        "loss": -2,
        "tie": 0,
        "win": 2
    },
    "training": {
        "discount_factor": 0.9,
        "estimated_optimal_future_value": "mean",
        "games_played": 8000,
        "games_to_play": 10000,
        "learning_rate": 0.05,
        "saving_rate": 1000
    }
}

store = NeuralStorage(config)
player = ReinforcementPlayer(store, config)

pr = cProfile.Profile()
pr.enable()
player.self_play_game()
pr.disable()
pr.print_stats(sort='time')
