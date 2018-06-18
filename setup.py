# -*- coding: utf-8 -*-
'''Setup script for StereoFlouroscopyRegistration package'''

# Imports
import re
from setuptools import setup, find_packages
from packaging import version

# Try to get version. Will throw error if something goes wrong.
VERSION = get_version()

# Verify version is PEP compliant
PEP440_REGEX = re.compile(version.VERSION_PATTERN, re.VERBOSE | re.IGNORECASE)
if PEP440_REGEX.match(VERSION) is None:
    raise EnvironmentError('Provided version \'{}\' is not PEP 440 compliant'.format(VERSION))

# Read in descripts
DESCRIPTION = 'An open source program for digitally reconstructed radiographs (DRR)'
with open('README.md') as long_description_file:
    LONG_DESCRIPTION = long_description_file.read()

# Final setup
setup(
    name='DRR-Studies',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://github.com/PayamZandiyeh/DRR-Studies/',
    author='Payam Zandiyeh',
    author_email='payam.zandiyeh@uth.tmc.edu',
    classifiers=[
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',

        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',

        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],

    packages=find_packages(
        exclude=[
            'pip',
            'config',
            'data',
            'demos',
            'tests',
        ]
    ),

    entry_points={
        'gui_scripts': [
        ],
    },
)
