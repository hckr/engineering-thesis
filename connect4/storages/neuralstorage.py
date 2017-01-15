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
    [ 0, 0, 0, 1, 2, 0, 1, 2, 1, 3 ]

    """
    return [field if field is not None else 0 for row in state.board for field in row] + [action]


class NeuralStorage:
    def __init__(self, config):
        self.rows = config['board']['rows']
        self.cols = config['board']['cols']
        self.net_file_path = config['neural_storage']['file_name']
        self.hidden_neurons = config['neural_storage']['hidden_neurons']
        self.net_input_size = self.rows * self.cols + 1
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
        bias = BiasUnit()
        hidden_layer = SigmoidLayer(self.hidden_neurons)
        out_layer = LinearLayer(1)

        n.addInputModule(in_layer)
        n.addModule(bias)
        n.addModule(hidden_layer)
        n.addOutputModule(out_layer)

        in_to_hidden = FullConnection(in_layer, hidden_layer)
        bias_to_hidden = FullConnection(bias, hidden_layer)
        hidden_to_out = FullConnection(hidden_layer, out_layer)

        n.addConnection(in_to_hidden)
        n.addConnection(bias_to_hidden)
        n.addConnection(hidden_to_out)

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
        return self.neural_net.activate(construct_net_input(state, action))[0]

    def update_value_of_action(self, player_id, state, action, learned_value):
        state = get_lookup_state(player_id, state)
        mirror_state = state.mirror()
        ds = SupervisedDataSet(self.net_input_size, 1)
        ds.addSample(construct_net_input(state, action), learned_value)
        if mirror_state != state:
            mirror_action = self.mirror_action(action)
            ds.addSample(construct_net_input(mirror_state, mirror_action), learned_value)
        self.trainer.trainOnDataset(ds)
