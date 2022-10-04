# Copyright (c) 2017, CapKPI Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import capkpi


class TestSoilTexture(unittest.TestCase):
	def test_texture_selection(self):
		soil_tex = capkpi.get_all(
			"Soil Texture", fields=["name"], filters={"collection_datetime": "2017-11-08"}
		)
		doc = capkpi.get_doc("Soil Texture", soil_tex[0].name)
		self.assertEqual(doc.silt_composition, 50)
		self.assertEqual(doc.soil_type, "Silt Loam")
