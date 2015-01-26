#!/usr/bin/env python2.7

from setuptools import setup, find_packages

setup(name = 'bust',
		version = '0.0',
		description = 'bus tracker app',
		author='Andy Tran',
		author_email = 'andy@atran.net',
		url = '',
		packages = find_packages(),
		include_package_data = True,
		zip_safe = False,
		install_requires = [
			'Flask',
			'requests',
			'lxml',
		],
		entry_points = {
			'console_scripts': [
				'bust-start = bust.main:main'
			]
		}
)


