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

from molmod.vectors import *

import numpy, copy
import unittest


__all__ = ["VectorTestCase"]


class VectorTestCase(BaseTestCase):
    def test_cosine(self):
        for i in xrange(100):
            a = numpy.random.normal(0,1,3)
            b = numpy.random.normal(0,1,3)
            cos = cosine(a,b)
            self.assert_(cos>=-1)
            self.assert_(cos<=1)
            cos = cosine(a,a)
            self.assertAlmostEqual(cos, 1)
            cos = cosine(a,-a)
            self.assertAlmostEqual(cos, -1)
            a /= numpy.linalg.norm(a)
            b /= numpy.linalg.norm(b)
            cos = cosine(a+b,a-b)
            self.assertAlmostEqual(cos, 0)

    def test_angle(self):
        for i in xrange(100):
            a = numpy.random.normal(0,1,3)
            b = numpy.random.normal(0,1,3)
            alpha = angle(a,b)
            self.assert_(alpha>=0.0)
            self.assert_(alpha<=numpy.pi)
            alpha = angle(a,a)
            self.assertAlmostEqual(alpha, 0.0)
            alpha = angle(a,-a)
            self.assertAlmostEqual(alpha, numpy.pi)
            a /= numpy.linalg.norm(a)
            b /= numpy.linalg.norm(b)
            alpha = angle(a+b,a-b)
            self.assertAlmostEqual(alpha, numpy.pi/2)

    def test_random_unit(self):
        for i in xrange(100):
            self.assertAlmostEqual(numpy.linalg.norm(random_unit(10)), 1.0)
            self.assertAlmostEqual(numpy.linalg.norm(random_unit()), 1.0)
            self.assertEqual(len(random_unit()), 3)

    def test_random_orthonormal(self):
        for i in xrange(100):
            a = numpy.random.normal(0,1,3)
            b = random_orthonormal(a)
            self.assertAlmostEqual(numpy.dot(a,b), 0)
            self.assertAlmostEqual(numpy.linalg.norm(b), 1)

    def test_triangle_normal(self):
        for i in xrange(100):
            a = numpy.random.normal(0,1,3)
            b = numpy.random.normal(0,1,3)
            c = numpy.random.normal(0,1,3)
            n = triangle_normal(a, b, c)
            self.assertAlmostEqual(numpy.dot(n, a-b), 0.0)
            self.assertAlmostEqual(numpy.dot(n, b-c), 0.0)
            self.assertAlmostEqual(numpy.dot(n, c-a), 0.0)
            self.assertAlmostEqual(numpy.linalg.norm(n), 1.0)
