#!/usr/bin/env bash

export CONFIG_PREFIX="stage_five_"
export NUMBER_OF_TRAININGS=5

cd `dirname "${BASH_SOURCE[0]}"`
./run_stage_generic.sh
