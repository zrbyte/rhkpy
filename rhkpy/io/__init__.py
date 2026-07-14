"""File input: loading RHK .sm4 files.

The sm4 reader lives in :mod:`rhkpy.io.sm4` (ported from the spym project,
which rhkpy previously depended on). The vendored spym copy in the repository
is retained only as a legacy reference for cross-validation in the test
suite; rhkpy itself no longer imports it.
"""

from . import sm4
from .sm4 import load_dataset


def load_rhksm4(filename):
	"""Load the .sm4 file into the low-level page container (historical name;
	uses rhkpy's built-in sm4 reader, ported from spym)."""
	return sm4.load(filename)


def load_spym(filename):
	"""Load the .sm4 file into an xarray Dataset (historical name; uses
	rhkpy's built-in sm4 reader, ported from spym)."""
	return load_dataset(filename)
