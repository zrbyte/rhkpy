"""Builders: turn the raw sm4 Dataset (`spymdata`) into the `image` and
`spectra` xarray Datasets of an rhkdata instance.

The `_load_*` dispatchers were moved verbatim from rhkpy_loader.py
(refactor phase 2).
"""

from ..analysis.ops import polyflatten

from .detect import _checkrepetitions, _checkdatatype, _aspect_ratio, _get_filename
from .spectra import _xr_map_iv, _xr_line_iv, _xr_spec_iv, _xr_map_iz, _xr_line_iz, _xr_spec_iz
from .image import _xr_image, _xr_image_line
from .metadata import _add_map_metadata, _add_line_metadata, _add_spec_metadata, _add_image_metadata


def _load_specmap(stmdata_object):
	# total number of spectra in one postion of the tip
	stmdata_object.numberofspectra = int((stmdata_object.alternate + 1)*stmdata_object.repetitions)
	# load the image
	stmdata_object = _load_image(stmdata_object)

	# decide if it's a dI/dV or I(z) map
	if stmdata_object.spectype == 'iv':
		# create a DataSet, containing the LIA and Current maps, with appropriate position coordinates
		stmdata_object = _xr_map_iv(stmdata_object)
		# add metadata to the xarray
		stmdata_object = _add_map_metadata(stmdata_object)
	elif stmdata_object.spectype == 'iz':
		# create xarray Dataset
		stmdata_object = _xr_map_iz(stmdata_object)
		# add metadata to the xarray
		stmdata_object = _add_map_metadata(stmdata_object)
	return stmdata_object

def _load_line(stmdata_object):
	# total number of spectra in one postion of the tip
	stmdata_object.numberofspectra = int((stmdata_object.alternate + 1)*stmdata_object.repetitions)
	# load the image data
	stmdata_object = _load_image(stmdata_object)

	# decide if it's a dI/dV or I(z) line
	if stmdata_object.spectype == 'iv':
		stmdata_object = _xr_line_iv(stmdata_object)
		stmdata_object = _add_line_metadata(stmdata_object)
	elif stmdata_object.spectype == 'iz':
		stmdata_object = _xr_line_iz(stmdata_object)
		stmdata_object = _add_spec_metadata(stmdata_object)
	return stmdata_object

def _load_spec(stmdata_object):
	# in this case the total number of spectra can be inferred
	# total number of spectra in one postion of the tip
	stmdata_object.repetitions = int(stmdata_object.spymdata.Current.data.shape[1] / (stmdata_object.alternate + 1))
	stmdata_object.numberofspectra = int((stmdata_object.alternate + 1)*stmdata_object.repetitions)

	# decide if it's a dI/dV or I(z) spec
	if stmdata_object.spectype == 'iv':
		stmdata_object = _xr_spec_iv(stmdata_object)
		stmdata_object = _add_spec_metadata(stmdata_object)
	elif stmdata_object.spectype == 'iz':
		stmdata_object = _xr_spec_iz(stmdata_object)
		stmdata_object = _add_spec_metadata(stmdata_object)
	return stmdata_object

def _load_image(stmdata_object):
	# load the image data
	if stmdata_object.datatype == 'image' or stmdata_object.datatype == 'map':
		stmdata_object = _xr_image(stmdata_object)
	elif stmdata_object.datatype == 'line':
		stmdata_object = _xr_image_line(stmdata_object)
	# add metadata
	stmdata_object = _add_image_metadata(stmdata_object)

	# make a polynomial background subtraction to the topography data (flatten)
	if stmdata_object.loadraw is False:
		stmdata_object.image = polyflatten(stmdata_object.image, polyorder = 1)
	return stmdata_object
