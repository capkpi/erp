# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
import re

from setuptools import find_packages, setup

# get version from __version__ variable in erp/__init__.py
_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

with open("erp/__init__.py", "rb") as f:
	version = str(ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1)))

setup(
	name="erp",
	version=version,
	description="Open Source ERP",
	author="CapKPI Technologies",
	author_email="info@capkpi.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
