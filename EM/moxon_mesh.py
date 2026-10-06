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
import math
import xlrd

import gmsh

#
try:
    index = int(sys.argv[1])
    
except:
    print(f'Usage: {os.path.basename(__file__)} <index>\n')
    sys.exit(1)

#
workbook = xlrd.open_workbook("Moxon.xls")
sheet = workbook.sheet_by_index(0)

ref = {}
for row_index in range(1, sheet.nrows):
    cell = sheet.cell_value(row_index, 0)

    if cell != '':
        ref[int(cell)] = row_index

# Units
inch = 0.0254

# Frequency and wavelength
c0 = 299792458.0
freq = 28e6
wavelength = c0/freq

# Moxon dimensions
r_1      = 0.3125*inch
r_2      =   0.25*inch
r_bend   =   1.50*inch
gap      =   0.75*inch

A1 = sheet.cell_value(ref[index], 1)*inch
A2 = sheet.cell_value(ref[index], 2)*inch
B = sheet.cell_value(ref[index], 3)*inch
C = sheet.cell_value(ref[index], 4)*inch
D = sheet.cell_value(ref[index], 5)*inch

print(f"Index: {index:03d}\n")
print(f"A1: {A1:>8.5f} meters")
print(f"A2: {A2:>8.5f} meters")
print(f" B: {B:>8.5f} meters")
print(f" C: {C:>8.5f} meters")
print(f" D: {D:>8.5f} meters")
print()

E =  (B+C+D+2*r_bend)

# Outer boundary
x_center = E/2.0
y_center = 0.0
air_radius = 1.0*wavelength

#
gmsh.initialize()
gmsh.model.add("moxon")

gmsh.model.setAttribute("Comments",
    [
        "Project: Moxon Antenna",
        "   freq: %.3f" % (freq/1.0E6),
        "     A1: %.7f" % (A1),
        "     A2: %.7f" % (A2),
        "      B: %.7f" % (B),
        "      C: %.7f" % (C),
        "      D: %.7f" % (D),
        "    r_1: %.7f" % (r_1),
        "    r_2: %.7f" % (r_2),
        " r_bend: %.7f" % (r_bend),
        "    gap: %.7f" % (gap),
    ]
)

occ = gmsh.model.occ

#
def fuse(parts):
    out, _ = occ.fuse([parts[0]], parts[1:])
    return out[0]

# Driven element: +y half
d1 = occ.addCylinder(0, gap/2, 0, 0, A1/2-gap/2, 0, r_1)
d2 = occ.addCylinder(0, A1/2,  0, 0, A2,         0, r_2)
d3 = occ.addTorus(r_bend, A1/2+A2, 0, r_bend, r_2, angle=math.pi/2)
occ.rotate([(3, d3)], r_bend, A1/2+A2, 0, 0, 0, 1, math.pi/2)
d4 = occ.addCylinder(r_bend, A1/2+A2+r_bend, 0, B, 0, 0, r_2)

driven_pos = fuse([(3, d1), (3, d2), (3, d3), (3, d4)])

# Driven element: -y half
d1 = occ.addCylinder(0, -gap/2, 0, 0, -(A1/2-gap/2), 0, r_1)
d2 = occ.addCylinder(0, -A1/2,  0, 0, -A2,           0, r_2)
d3 = occ.addTorus(r_bend, -(A1/2+A2), 0, r_bend, r_2, angle=math.pi/2)
occ.rotate([(3, d3)], r_bend, -(A1/2+A2), 0, 0, 0, 1, math.pi)
d4 = occ.addCylinder(r_bend, -(A1/2+A2+r_bend), 0, B, 0, 0, r_2)

driven_neg = fuse([(3, d1), (3, d2), (3, d3), (3, d4)])

# Reflector
r1 = occ.addCylinder(E, -A1/2, 0, 0,  A1, 0, r_1)
r2 = occ.addCylinder(E,  A1/2, 0, 0,  A2, 0, r_2)
r3 = occ.addCylinder(E, -A1/2, 0, 0, -A2, 0, r_2)
r4 = occ.addTorus(E-r_bend, -(A1/2+A2), 0, r_bend, r_2, angle=math.pi/2)
occ.rotate([(3, r4)], E-r_bend, -(A1/2+A2), 0, 0, 0, 1, -math.pi/2)
r5 = occ.addCylinder(E-r_bend, -(A1/2+A2+r_bend), 0, -D, 0, 0, r_2)
r6 = occ.addTorus(E-r_bend, (A1/2+A2), 0, r_bend, r_2, angle=math.pi/2)
r7 = occ.addCylinder(E-r_bend,  (A1/2+A2+r_bend), 0, -D, 0, 0, r_2)

reflector = fuse([(3, r1), (3, r2), (3, r3), (3, r4), (3, r5), (3, r6), (3, r7)])

# Feed sheet and outer sphere
port = occ.addRectangle(-r_2, -gap/2, 0, 2*r_2, gap)
sphere = occ.addSphere(x_center, y_center, 0, air_radius)

# Fragmentation
out_dimtags, out_map = occ.fragment([(3, sphere)], [driven_pos, driven_neg, reflector, (2, port)])

occ.synchronize()

sphere_parts     = out_map[0]
driven_pos_parts = out_map[1]
driven_neg_parts = out_map[2]
reflector_parts  = out_map[3]
port_parts       = out_map[4]

conductor_parts = driven_pos_parts+driven_neg_parts+reflector_parts
conductor_tags = [tag for dim, tag in conductor_parts if dim == 3]

air_parts = [entity for entity in sphere_parts if entity not in conductor_parts]
air_tags = [tag for dim, tag in air_parts if dim == 3]

port_tags = [tag for dim, tag in port_parts if dim == 2]

pec_tags = []
for part in conductor_parts:
    entities =  gmsh.model.getBoundary([part], oriented=False, recursive=False)

    for dim, tag in entities:
        if (dim == 2) and (tag not in port_tags):
            pec_tags.append(tag)

outer_tags = []
entities = gmsh.model.getBoundary(air_parts, oriented=False, recursive=False)
for dim, tag in entities:
    if dim == 2:
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)

        if abs((xmax-xmin)-2*air_radius) < 0.01*air_radius:
            outer_tags.append(tag)

# Physical groups used by Palace
gmsh.model.addPhysicalGroup(3, air_tags, 1, "air")
gmsh.model.addPhysicalGroup(2, pec_tags, 2, "pec")
gmsh.model.addPhysicalGroup(2, port_tags, 3, "port")
gmsh.model.addPhysicalGroup(2, outer_tags, 4, "farfield")
gmsh.model.addPhysicalGroup(3, conductor_tags, 5, "conductor")

# Mesh
n_circle = 8
n_farfield = 3

gmsh.option.setNumber("Mesh.MeshSizeMin", 2.0*math.pi*r_2/n_circle/2.0)
gmsh.option.setNumber("Mesh.MeshSizeMax", wavelength/n_farfield)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", n_circle)
gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
gmsh.option.setNumber("Mesh.Algorithm", 6)
gmsh.option.setNumber("Mesh.Algorithm3D", 1)
gmsh.option.setNumber("Mesh.RandomSeed", 1)

gmsh.model.mesh.field.add("Extend", 1)
gmsh.model.mesh.field.setAsBackgroundMesh(1)

gmsh.model.mesh.field.setNumbers(1, "SurfacesList", pec_tags+port_tags)
gmsh.model.mesh.field.setNumber(1, "DistMax", air_radius)
gmsh.model.mesh.field.setNumber(1, "SizeMax", wavelength/n_farfield)

gmsh.model.mesh.generate(3)

os.makedirs('%03d' % (index), exist_ok=True)

gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.option.setNumber("Mesh.Binary", 1)
gmsh.write("%03d/moxon.msh" % (index))

gmsh.option.setNumber("Mesh.StlOneSolidPerSurface", 1)
gmsh.option.setNumber("Mesh.Binary", 0)
gmsh.write("%03d/moxon.stl" % (index))

#
gmsh.finalize()
