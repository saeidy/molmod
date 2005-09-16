# PyChem is a general chemistry oriented python package.
# Copyright (C) 2005 Toon Verstraelen
# 
# This file is part of PyChem.
# 
# PyChem is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
# --

from pychem.internal_coordinates import Collection
from pychem.molecular_graphs import BondSets, BondAngleSets, DihedralAngleSets, CriteriaSet
from pychem.molecules import molecule_from_xyz_filename
from pychem.moldata import BOND_SINGLE
from pychem.units import from_angstrom

import unittest, math, Numeric


__all__ = ["suite"]

suite = unittest.TestSuite()   

class TestDihedralChainrule(unittest.TestCase):        
    def test_dihedral_chainrule(self):
        ethene = molecule_from_xyz_filename("input/ethene.xyz")
        ethene_mod = molecule_from_xyz_filename("input/ethene_mod.xyz")

        # Define a set of independant internal coordinates.
        collection = Collection(ethene)
        collection.add_dihedral_angles(DihedralAngleSets([CriteriaSet("HCCH-angles", ((1, 6, 6, 1), None))]))
        dihedral = collection["HCCH-angles"][0]
        value, gradient = dihedral(ethene.coordinates)
        delta = ethene.coordinates - ethene_mod.coordinates 
        cos_estimate = Numeric.dot(Numeric.ravel(gradient), Numeric.ravel(delta))
        cos_real = math.cos(90.0/180.0*math.pi)-math.cos(80.0/180.0*math.pi)
        self.assertAlmostEqual(
            cos_real, 
            cos_estimate, 
            5, 
            "Difference in estimate and real cosine: %f-%f=%f" % (cos_estimate, cos_real, cos_estimate-cos_real)
        )

suite.addTests([
    unittest.makeSuite(TestDihedralChainrule)
])