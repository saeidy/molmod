# -*- coding: utf-8 -*-
# MolMod is a collection of molecular modelling tools for python.
# Copyright (C) 2007 - 2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
# for Molecular Modeling (CMM), Ghent University, Ghent, Belgium; all rights
# reserved unless otherwise stated.
#
# This file is part of MolMod.
#
# MolMod is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# MolMod is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
#--


from common import BaseTestCase

from molmod.io.xyz import *
from molmod.units import angstrom

import numpy as np, unittest


__all__ = ["XYZTestCase"]


class XYZTestCase(BaseTestCase):
    def test_xyz_reader(self):
        xr = XYZReader("input/water.xyz")
        mol = xr.get_first_molecule()
        self.assertEqual(mol.symbols, ("O", "H", "H"))
        self.assertArraysEqual(mol.numbers, np.array([8,1,1]))
        self.assertEqual(mol.title, "water")
        self.assertAlmostEqual(mol.coordinates[0,0]/angstrom, -0.0914980466)
        self.assertAlmostEqual(mol.coordinates[2,2]/angstrom, -0.7649930856)
        self.assertEqual(xr.symbols, ("O", "H", "H"))
        self.assertArraysEqual(xr.numbers, np.array([8,1,1]))
        title, coordinates = xr.next()
        self.assertEqual(title, "water")
        self.assertAlmostEqual(coordinates[0,0]/angstrom, -0.0914980466)
        self.assertAlmostEqual(coordinates[2,2]/angstrom, -0.7649930856)

    def test_xyz_writer(self):
        xr = XYZReader("input/water.xyz")
        xw = XYZWriter("output/test.xyz", xr.symbols)
        for title, coordinates in xr:
            xw.dump(title, coordinates)
        del xw
        xr = XYZReader("output/test.xyz")
        self.assertEqual(xr.symbols, ("O", "H", "H"))
        self.assertArraysEqual(xr.numbers, np.array([8,1,1]))
        title, coordinates = xr.next()
        self.assertEqual(title, "water")
        self.assertAlmostEqual(coordinates[0,0]/angstrom, -0.0914980466)
        self.assertAlmostEqual(coordinates[2,2]/angstrom, -0.7649930856)

    def test_xyz_file(self):
        xf = XYZFile("input/water.xyz")
        self.assertEqual(xf.symbols, ("O", "H", "H"))
        self.assertArraysEqual(xf.numbers, np.array([8,1,1]))
        self.assertEqual(xf.titles[0], "water")
        self.assertAlmostEqual(xf.geometries[0,0,0]/angstrom, -0.0914980466)
        self.assertAlmostEqual(xf.geometries[0,2,2]/angstrom, -0.7649930856)
        xf.geometries = np.array([xf.geometries[0]]*10)
        xf.titles = [xf.titles[0]]*10
        xf.write_to_file("output/test.xyz")
        xf = XYZFile("output/test.xyz")
        self.assertEqual(xf.symbols, ("O", "H", "H"))
        self.assertArraysEqual(xf.numbers, np.array([8,1,1]))
        self.assertEqual(xf.titles[0], "water")
        self.assertAlmostEqual(xf.geometries[0,0,0]/angstrom, -0.0914980466)
        self.assertAlmostEqual(xf.geometries[0,2,2]/angstrom, -0.7649930856)
        xf = XYZFile("output/test.xyz", slice(0,9,2))
        self.assertEqual(xf.symbols, ("O", "H", "H"))
        self.assertArraysEqual(xf.numbers, np.array([8,1,1]))
        self.assertEqual(xf.titles[0], "water")
        self.assertAlmostEqual(xf.geometries[0,0,0]/angstrom, -0.0914980466)
        self.assertAlmostEqual(xf.geometries[0,2,2]/angstrom, -0.7649930856)

    def test_probes(self):
        xyz = XYZFile("input/probes.xyz")
        self.assertEqual(xyz.numbers[-1], 0)

    def test_dopamine(self):
        xyz = XYZFile("input/dopamine.xyz")
        self.assertEqual(xyz.symbols[0], "O")
        self.assertEqual(xyz.numbers[0], 8)
        self.assertEqual(xyz.symbols[5], "C")
        self.assertEqual(xyz.numbers[5], 6)
        self.assertEqual(xyz.symbols[-1], "H")
        self.assertEqual(xyz.numbers[-1], 1)
