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
