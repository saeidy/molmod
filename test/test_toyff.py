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


from molmod.toyff import guess_geometry, tune_geometry, ToyFF
from molmod.molecules import Molecule
from molmod.molecular_graphs import MolecularGraph
from molmod.unit_cells import UnitCell
from molmod.units import angstrom

import unittest, numpy, os


__all__ = ["ToyFFTestCase"]


class ToyFFTestCase(unittest.TestCase):
    def load_molecule(self, fn):
        molecule = Molecule.from_file(os.path.join("input", fn))
        if molecule.graph is None:
            molecule.set_default_graph()
        return molecule

    def iter_molecules(self, allow_multi=False):
        fns = [
          "water.xyz", "cyclopentane.xyz", "ethene.xyz", "funny.xyz",
          "tea.xyz", "tpa.xyz", "thf_single.xyz", "precursor.xyz",
          "butane.xyz", "octane.xyz","example.sdf", "CID_22898828.sdf",
          "SID_55127927.sdf", "SID_56274343.sdf", "SID_40363570.sdf",
          "SID_40363571.sdf", "SID_31646548.sdf", "SID_31646545.sdf",
          "SID_41893278.sdf", "SID_41893280.sdf", "SID_54258192.sdf",
          "SID_55488598.sdf",
        ]
        for fn in fns:
            molecule = self.load_molecule(fn)
            if allow_multi or len(molecule.graph.independent_vertices) == 1:
                yield molecule

    def test_guess_geometry(self):
        for input_mol in self.iter_molecules(allow_multi=False):
            output_mol = guess_geometry(input_mol.graph)
            output_mol.title = input_mol.title
            output_mol.write_to_file("output/guess_%s.xyz" % input_mol.title)

    def test_tune_geometry(self):
        for input_mol in self.iter_molecules(allow_multi=False):
            output_mol = tune_geometry(input_mol.graph, input_mol)
            output_mol.title = input_mol.title
            output_mol.write_to_file("output/tune_%s.xyz" % input_mol.title)

    def get_random_ff(self):
        N = 6

        mask = numpy.zeros((N,N), bool)
        for i in xrange(N):
            for j in xrange(i):
                mask[i,j] = True

        from molmod.ext import molecules_distance_matrix
        while True:
            unit_cell = UnitCell(
                numpy.random.uniform(0,3,(3,3)),
                numpy.random.randint(0,2,3).astype(bool),
            )
            fractional = numpy.random.uniform(0,1,(N,3))
            coordinates = unit_cell.to_cartesian(fractional)
            if numpy.random.randint(0,2):
                unit_cell = None
                dm = molecules_distance_matrix(coordinates)
            else:
                dm = molecules_distance_matrix(coordinates, unit_cell.matrix, unit_cell.reciprocal)
            if dm[mask].min() > 1.0:
                break


        edges = set([])
        while len(edges) < 2*N:
            v1 = numpy.random.randint(N)
            while True:
                v2 = numpy.random.randint(N)
                if v2 != v1:
                    break
            edges.add(frozenset([v1,v2]))
        edges = tuple(edges)
        numbers = numpy.random.randint(6, 10, N)
        graph = MolecularGraph(edges, numbers)
        ff = ToyFF(graph, unit_cell)

        return ff, coordinates, dm, mask, unit_cell

    def check_toyff_gradient(self, ff, coordinates):
        energy0, gradient0 = ff(coordinates, True)
        eps = numpy.random.uniform(-1e-6, 1e-6, coordinates.shape)
        energy1, gradient1 = ff(coordinates+eps, True)

        delta_energy = energy1 - energy0
        approx_delta_energy = 0.5*numpy.dot(gradient0 + gradient1, eps.ravel())

        error = abs(delta_energy - approx_delta_energy)
        oom = abs(delta_energy)

        self.assert_(error < oom*1e-5)

    def test_dm_quad_energy(self):
        for i in xrange(10):
            ff, coordinates, dm, mask, unit_cell = self.get_random_ff()
            ff.dm_quad = 1.0
            energy = ff(coordinates, False)
            my_terms = (dm - ff.dm0)**2*ff.dmk
            my_terms[ff.dm0==0] = 0.0
            my_terms[mask] = 0.0
            self.assertAlmostEqual(energy, my_terms.sum())

    def test_dm_quad_gradient(self):
        for i in xrange(10):
            ff, coordinates, dm, mask, unit_cell = self.get_random_ff()
            ff.dm_quad = 1.0
            self.check_toyff_gradient(ff, coordinates)

    def test_dm_reci_energy(self):
        for i in xrange(10):
            ff, coordinates, dm, mask, unit_cell = self.get_random_ff()
            ff.dm_reci = 1.0
            energy = ff(coordinates, False)
            r0 = numpy.add.outer(ff.vdw_radii, ff.vdw_radii)
            d = dm/r0
            numpy.ravel(d)[::len(d)+1] = 1.0
            my_terms = (d-1)*(d-1)/d
            my_terms[ff.dm<=1] = 0.0
            my_terms[d>=1] = 0.0
            my_terms[mask] = 0.0
            self.assertAlmostEqual(energy, my_terms.sum())

    def test_dm_reci_gradient(self):
        for i in xrange(10):
            ff, coordinates, dm, mask, unit_cell = self.get_random_ff()
            ff.dm_reci = 1.0
            self.check_toyff_gradient(ff, coordinates)

    def test_bond_quad_energy(self):
        for i in xrange(10):
            ff, coordinates, dm, mask, unit_cell = self.get_random_ff()
            ff.bond_quad = 1.0
            energy = ff(coordinates, False)
            lengths = numpy.array([dm[i,j] for i,j in ff.bond_edges])
            my_terms = (lengths - ff.bond_lengths)**2
            self.assertAlmostEqual(energy, my_terms.sum())

    def test_bond_quad_gradient(self):
        for i in xrange(10):
            ff, coordinates, dm, mask, unit_cell = self.get_random_ff()
            ff.bond_quad = 1.0
            self.check_toyff_gradient(ff, coordinates)

    def test_bond_hyper_energy(self):
        for i in xrange(10):
            ff, coordinates, dm, mask, unit_cell = self.get_random_ff()
            ff.bond_hyper = 1.0
            energy = ff(coordinates, False)
            lengths = numpy.array([dm[i,j] for i,j in ff.bond_edges])
            my_terms = numpy.cosh((lengths - ff.bond_lengths)*ff.bond_hyper_scale)-1
            self.assertAlmostEqual(energy/my_terms.sum(), 1.0)

    def test_bond_hyper_gradient(self):
        for i in xrange(10):
            ff, coordinates, dm, mask, unit_cell = self.get_random_ff()
            ff.bond_hyper = 1.0
            self.check_toyff_gradient(ff, coordinates)

    def test_example_periodic(self):
        mol = Molecule.from_file("input/caplayer.cml")
        unit_cell = UnitCell(
            numpy.array([
                [14.218,  7.109,  0.0],
                [ 0.0  , 12.313,  0.0],
                [ 0.0  ,  0.0  , 10.0],
            ])*angstrom,
            numpy.array([True, True, False]),
        )
        dm = mol.distance_matrix
        dm = dm + dm.max()*numpy.identity(len(dm))
        mol = tune_geometry(mol.graph, mol, unit_cell)
        mol.write_to_file("output/caplayer.xyz")
