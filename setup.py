import os
from setuptools import setup, find_packages


PYPI_RESTRUCTURED_TEXT_INFO = \
"""
Basic Example
-------------

::

	from assembla import API

	assembla = API(
	    key='8a71541e5fb2e4741120',
	    secret='a260dc4448c81c907fc7c85ad09d31306c425417',
	    # Auth details from https://www.assembla.com/user/edit/manage_clients
	)

	my_space = assembla.spaces(name='My Space')[0]

	for ticket in my_space.tickets():
	    print '#{0} - {1}'.format(ticket['number'], ticket['summary'])

	# >>> #1 - My first ticket
	# >>> #2 - My second ticket
	# ...

Full documentation at http://github.com/markfinger/assembla
"""

setup(
    name = 'assembla',
    version = '2.0.0',
    packages = find_packages(),

    install_requires = [
        'requests==1.0.4',
    ],
    package_data = {'assembla': []},
    entry_points = {},

    # metadata for upload to PyPI
    author = 'Mark Finger',
    author_email = 'markfinger@gmail.com',
    description = 'Python wrapper for the Assembla API',
    license = 'CC BY 3.0',
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
    ],
)
