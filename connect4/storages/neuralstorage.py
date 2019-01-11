# -*- coding: utf-8 -*-

import os.path
from pybrain.structure import FeedForwardNetwork, LinearLayer, SigmoidLayer, FullConnection, BiasUnit
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader
import numpy as np
import sys

THIS_DIR = os.path.dirname(__file__)
STORED_DATA_DIR = os.path.join(THIS_DIR, 'stored_data')


def get_lookup_state(player_id, state):
    if player_id == 1:
        return state
    else:
        return state.switch_players()


def construct_net_input(state, action):
    """ Constructs list which can be used as input to neural net.

    Example input:

    state.board = [[ None, None, None ],
                   [    1,    2, None ],
                   [    1,    2,    1 ]]

    action = 3

    Example output:
    ???

    """
    board = []
    for row in state.board:
        for field in row:
            if field == 1:
                board += [1, 0, 0]
            elif field == 2:
                board += [0, 1, 0]
            else:
                board += [0, 0, 1]
    actions = [1 if action == i else 0 for i in range(len(state.board[0]))]
    return board + actions


class NeuralStorage:
    def __init__(self, config):
        self.rows = config['board']['rows']
        self.cols = config['board']['cols']
        self.net_file_path = config['neural_storage']['file_name']
        self.hidden_neurons = config['neural_storage']['hidden_neurons']
        self.net_input_size = self.rows * self.cols * 3 + self.cols
        if os.path.isfile(self.net_file_path):
            self.load_neural_net()
        else:
            sys.stderr.write('[NeuralStorage] creating new neural net\n')
            self.init_neural_net()
            self.set_random_weights(-1, 1)
        self.trainer = BackpropTrainer(self.neural_net, learningrate=config['learning_rate'])

    def init_neural_net(self):
        n = FeedForwardNetwork()

        in_layer = LinearLayer(self.net_input_size)
        biases = [BiasUnit() for x in range(len(self.hidden_neurons) + 1)]
        hidden_layers = [SigmoidLayer(x) for x in self.hidden_neurons]
        out_layer = LinearLayer(1)

        n.addInputModule(in_layer)
        for i in range(len(hidden_layers)):
            n.addModule(biases[i])
            n.addModule(hidden_layers[i])
        n.addOutputModule(out_layer)
        n.addModule(biases[-1])

        n.addConnection(FullConnection(in_layer, hidden_layers[0]))
        for i in range(len(hidden_layers)):
            n.addConnection(FullConnection(biases[i], hidden_layers[i]))
        for i in range(len(hidden_layers) - 1):
            n.addConnection(FullConnection(hidden_layers[i], hidden_layers[i+1]))
        n.addConnection(FullConnection(hidden_layers[-1], out_layer))
        n.addConnection(FullConnection(biases[-1], out_layer))

        n.sortModules()
        self.neural_net = n

    def set_random_weights(self, range_beginning, range_end):
        params_len = len(self.neural_net.params)
        range_size = range_end - range_beginning
        self.neural_net._setParameters(np.random.random(params_len) * range_size - (range_size / 2))

    def load_neural_net(self):
        self.neural_net = NetworkReader.readFrom(self.net_file_path)

    def save(self):
        NetworkWriter.writeToFile(self.neural_net, self.net_file_path)

    def mirror_action(self, action):
        return self.cols - 1 - action

    def get_value_of_action(self, player_id, state, action):
        state = get_lookup_state(player_id, state)
        val = self.neural_net.activate(construct_net_input(state, action))[0]
        return val

    def update_value_of_action(self, player_id, state, action, learned_value):
        state = get_lookup_state(player_id, state)
        mirror_state = state.mirror()
        ds = SupervisedDataSet(self.net_input_size, 1)
        ds.addSample(construct_net_input(state, action), learned_value)
        if mirror_state != state:
            mirror_action = self.mirror_action(action)
            ds.addSample(construct_net_input(mirror_state, mirror_action), learned_value)
        self.trainer.trainOnDataset(ds)
