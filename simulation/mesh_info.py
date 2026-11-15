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
import gmsh

#
try:
    filename = sys.argv[1]

except:
    print(f'Usage: {os.path.basename(__file__)} <filename>\n')
    sys.exit(1)

#
gmsh.initialize()
gmsh.open(filename)

print()

for name in gmsh.model.getAttributeNames():
    print(f'[{name}]')

    for value in gmsh.model.getAttribute(name):
        print(value)

gmsh.finalize()
