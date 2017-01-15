#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

latex_special = "_%"


def prepare(s):
    ret = s.strip()
    for c in latex_special:
        ret = ret.replace(c, r'\%s' % c)
    return ret


with open(sys.argv[1]) as file:
    contents = file.read()

name = sys.argv[1].rsplit('.')[0]
rankings = contents.split('\n\n\n')

print(r'\begin{longtable}[c]{|r|c|c|c|}')
print(r'\caption{\label{tab:%s}%s} \\' % (name, prepare(name)))

header = ''
header += '\n'
header += r'\multirow{2}{*}{\textbf{Nazwa konfiguracji}} & \multicolumn{3}{|c|}{\textbf{Procent wygranych gier}} \\'
header += '\n\\cline{2-4}\n'
header += r'&\textbf{średni} & \textbf{max} & \textbf{min} \\'

index = 1

for ranking in rankings:
    if ranking == '':
        continue

    print('\hline')
    print(header)

    for training_name, percent_won in [[prepare(s) for s in line.rsplit('-', 1)] for line in ranking.splitlines()]:
        print('\hline')
        mean, max, min = re.findall(r'\d{2}.\d{2}\\%', percent_won)
        print(training_name.replace('reinforcement-', ''), '&', mean, '&', max, '&', min, r'\\')

    print('\hline')

    index += 1

print('\end{longtable}')
