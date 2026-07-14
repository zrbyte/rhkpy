"""File input: loading RHK .sm4 files.

Currently delegates to the vendored spym package; the sm4 reader will be
reimplemented here (refactor phase 4), keeping spym as a legacy loader for
cross-validation in the test suite.
"""

from spym.io import load as _spym_load
from spym.io import rhksm4 as _spym_rhksm4


def load_rhksm4(filename):
	"""Load the data from the .sm4 file using the old loader from spym"""
	return _spym_rhksm4.load(filename)


def load_spym(filename):
	"""Load the data from the .sm4 file using spym"""
	return _spym_load(filename)
