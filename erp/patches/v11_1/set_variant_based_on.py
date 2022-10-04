# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import capkpi


def execute():
	capkpi.db.sql(
		"""update tabItem set variant_based_on = 'Item Attribute'
		where ifnull(variant_based_on, '') = ''
		and (has_variants=1 or ifnull(variant_of, '') != '')
	"""
	)
