#!/usr/bin/env python3
# Copyright (C) 2026 Noyan Kinayman, KC1VCN
#
# This file is part of the KC1VCN 10-meter Moxon Antenna project.
#
# This source describes Open Hardware and is licensed under the
# CERN Open Hardware Licence Version 2 - Weakly Reciprocal
# (CERN-OHL-W-2.0).
#
# You may redistribute and modify this source and make products
# using it under the terms of CERN-OHL-W-2.0.
#
# This source is distributed WITHOUT ANY EXPRESS OR IMPLIED WARRANTY,
# INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS
# FOR A PARTICULAR PURPOSE. Please see the CERN-OHL-W-2.0 licence
# for applicable conditions.
#
# SPDX-License-Identifier: CERN-OHL-W-2.0
#
import sys
import os
import json
import subprocess

#
try:
    index = int(sys.argv[1])
    setup = int(sys.argv[2])
    dry_run = int(sys.argv[3])

except:
    print(f'Usage: {os.path.basename(__file__)} <index> <setup> <dry_run>\n')
    sys.exit(1)

#
print('Index: %d' % (index))

path = '%03d' % (index)
os.makedirs('%s' % (path), exist_ok=True)

filename = '%s/moxon.json' % (path)

#
if (setup):
    with open('moxon.json', 'r') as f:
        config = json.load(f)

    config['Model']['Mesh'] = '%s/moxon.msh' % (path)
    config['Problem']['Output'] = '%s' % (path)

    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)

#
if (dry_run):
    subprocess.run(['palace', '--dry-run', filename], check=True)

else:
    subprocess.run(['nice', '-n', '3', 'palace', '-np', '4', '--launcher-args', '--use-hwthread-cpus --bind-to hwthread', filename], check=True)

