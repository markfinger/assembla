import os
from setuptools import setup, find_packages

PYPI_RESTRUCTURED_TEXT_INFO = \
"""
====================================================
Assembla: Python wrapper for Assembla's API
====================================================

An easy to use wrapper around the Assembla API.

Basic Example
-------------

::

	from assembla import API

	assembla = API(auth=('Username', 'Password',))

	print assembla.space(name='Big Project').ticket(number=201).status_name


More documentation and source at http://github.com/markfinger/assembla
"""

setup(
    name = 'assembla',
    version = '1.2.1',
    packages = find_packages(),

    install_requires = [
        'requests>=0.7.4',
        'lxml>=2.3.1',
    ],
    package_data = {'assembla': []},
    entry_points = {},

    # metadata for upload to PyPI
    author = 'Mark Finger',
    author_email = 'markfinger@gmail.com',
    description = 'An easy to use wrapper around the Assembla API',
    license = 'BSD',
    platforms=['any'],
    keywords = 'Assembla API',
    url = 'http://github.com/markfinger/assembla/',
    long_description = PYPI_RESTRUCTURED_TEXT_INFO,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
    ],
)
