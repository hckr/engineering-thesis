#!/usr/bin/env bash

if [ "$CONFIG_PREFIX" == "" ]
then
    echo '$CONFIG_PREFIX is not defined!'
    exit
fi

if [ "$NUMBER_OF_TRAININGS" == "" ] || [ "$NUMBER_OF_TRAININGS" -lt 1 ]
then
    echo '$NUMBER_OF_TRAININGS should be greater than zero!'
    exit
fi

existing_training_data=`../../agents_duel.py -d | grep ${CONFIG_PREFIX}`

if [ "$existing_training_data" != "" ]
then
    echo "It looks like this script was already executed."
    echo "The following training data is available:"
    echo "$existing_training_data"
    echo "You can delete old training data using reinforcement_train.py from the root project folder."
    echo "Exiting."
    exit
fi

MAX_PARALLEL=4
processes_run=0

for file in `ls ../reinf_configs/${CONFIG_PREFIX}*`
do
    for (( i=1; i<=$NUMBER_OF_TRAININGS; i++ ))
    do
        command="../../reinforcement_train.py $file"
        log_name_prefix=`basename ${file}`_${i}
        echo "$i: $command"
        > ${log_name_prefix}_output.txt
        > ${log_name_prefix}_log.txt
        { time ${command} >> ${log_name_prefix}_output.txt; } 2>> ${log_name_prefix}_log.txt &
        sleep 1
        let processes_run+=1
        (( processes_run%MAX_PARALLEL==0 )) && echo "Waiting for ${MAX_PARALLEL} processes to end..." && wait
    done
done

wait
