# Copyright (c) 2015, CapKPI Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

test_dependencies = ["Employee"]

import capkpi

test_records = capkpi.get_test_records("Sales Person")

test_ignore = ["Item Group"]
