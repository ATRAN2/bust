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
        'flask-cors',
        'lxml',
        'rtree',
        'requests',
        'Flask',
    ],
    entry_points = {
        'console_scripts': [
            'bust-start = bust.app:run_app',
			'bust-build = scripts.build_datastore:create_datastore_from_nextbus_to_file',
        ]
    }
)


