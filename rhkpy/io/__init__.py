"""File input: loading RHK .sm4 files.

The sm4 reader lives in :mod:`rhkpy.io.sm4` (ported from the spym project,
which rhkpy previously depended on). The vendored spym copy in the repository
is retained only as a legacy reference for cross-validation in the test
suite; rhkpy itself no longer imports it.
"""

from . import sm4
from .sm4 import load_dataset


def load_rhksm4(filename):
	"""Load the .sm4 file into the low-level page container.
	This is the historical name; it uses rhkpy's built-in sm4 reader (:mod:`rhkpy.io.sm4`, ported from spym).

	:param filename: path and filename of the "sm4" file to be loaded
	:type filename: str

	:return: container of the pages in the .sm4 file, with their raw data and metadata
	:rtype: :class:`rhkpy.io.sm4.RHKsm4`

	:Example:

		.. code-block:: python

			import rhkpy

			f = rhkpy.load_rhksm4('topography.sm4')
			p0 = f[0]  # first page in the file
			p0.label   # page label name
			p0.data    # page data as a numpy array
			p0.attrs   # page metadata as a dictionary
	"""
	return sm4.load(filename)


def load_spym(filename):
	"""Load the .sm4 file into an :py:mod:`xarray` Dataset.
	This is the historical name; it uses rhkpy's built-in sm4 reader (:mod:`rhkpy.io.sm4`, ported from spym).
	This is the Dataset found in the ``spymdata`` variable of an :class:`~rhkpy.rhkpy_loader.rhkdata` instance.

	:param filename: path and filename of the "sm4" file to be loaded
	:type filename: str

	:return: Dataset with one DataArray per page of the .sm4 file, or `None` if the file is not valid
	:rtype: :py:mod:`xarray` Dataset
	"""
	return load_dataset(filename)
