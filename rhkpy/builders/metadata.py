"""Attach measurement metadata (bias, setpoint, lock-in settings, ...) to the
constructed xarray Datasets.

One parametrized function covers all spectra types; the historical
``_add_map_metadata`` / ``_add_line_metadata`` / ``_add_spec_metadata``
entry points are kept as thin wrappers. Output is bit-identical to
rhkpy <= 1.3 (verified by the golden-master characterization tests).
"""


def _add_spectra_metadata(stmdata_object, scan_angle = True, bias_coord_units = False):
	"""Attach measurement metadata to the `spectra` Dataset.

	:param scan_angle: include the 'scan angle' attribute (available when the
		file also contains an image; historically omitted for single spectra)
	:param bias_coord_units: set units on the 'bias' coordinate (historically
		only done for single-point/line I(V) spectra)
	"""
	spym_current = stmdata_object.spymdata.Current
	spectra = stmdata_object.spectra

	if stmdata_object.spectype == 'iv':
		spectra['lia'].attrs['bias'] = spym_current.attrs['bias']
		spectra['lia'].attrs['bias units'] = 'V'
		spectra['lia'].attrs['setpoint'] = spym_current.attrs['RHK_Current']*10**12
		spectra['lia'].attrs['setpoint units'] = 'pA'
		spectra['lia'].attrs['time_per_point'] = spym_current.attrs['time_per_point']
		if bias_coord_units:
			spectra.coords['bias'].attrs['units'] = 'V'
			spectra.coords['bias'].attrs['long units'] = 'volt'

	spectra['current'].attrs['bias'] = spym_current.attrs['bias']
	spectra['current'].attrs['bias units'] = 'V'
	spectra['current'].attrs['setpoint'] = spym_current.attrs['RHK_Current']*10**12
	spectra['current'].attrs['setpoint units'] = 'pA'
	spectra['current'].attrs['time_per_point'] = spym_current.attrs['time_per_point']

	spectra.attrs['bias'] = spym_current.attrs['bias']
	spectra.attrs['bias units'] = 'V'
	spectra.attrs['setpoint'] = spym_current.attrs['RHK_Current']*10**12
	spectra.attrs['setpoint units'] = 'pA'
	spectra.attrs['measurement date'] = spym_current.attrs['RHK_Date']
	spectra.attrs['measurement time'] = spym_current.attrs['RHK_Time']
	if scan_angle:
		spectra.attrs['scan angle'] = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Angle']
	spectra.attrs['LI amplitude'] = spym_current.attrs['RHK_CH1Drive_Amplitude']*10**3
	spectra.attrs['LI amplitude unit'] = 'mV'
	spectra.attrs['LI frequency'] = spym_current.attrs['RHK_CH1Drive_Frequency']
	spectra.attrs['LI frequency unit'] = 'Hz'
	spectra.attrs['LI phase'] = spym_current.attrs['RHK_Lockin0_PhaseOffset']

	# store the data and spectrum type in the attributes
	spectra.attrs['datatype'] = stmdata_object.datatype
	spectra.attrs['spectype'] = stmdata_object.spectype

	return stmdata_object


## historical entry points --------------------------------------------

def _add_map_metadata(stmdata_object):
	return _add_spectra_metadata(stmdata_object, scan_angle = True)


def _add_line_metadata(stmdata_object):
	return _add_spectra_metadata(stmdata_object, scan_angle = True)


def _add_spec_metadata(stmdata_object):
	return _add_spectra_metadata(stmdata_object, scan_angle = False, bias_coord_units = True)


def _add_image_metadata(stmdata_object):
	stmdata_object.image.attrs['bias'] = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Bias']
	stmdata_object.image.attrs['bias units'] = 'V'
	stmdata_object.image.attrs['setpoint'] = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Current']*10**12
	stmdata_object.image.attrs['setpoint units'] = 'pA'
	stmdata_object.image.attrs['measurement date'] = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Date']
	stmdata_object.image.attrs['measurement time'] = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Time']
	stmdata_object.image.attrs['scan angle'] = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Angle']

	# store the data and spectrum type in the attributes
	# in the case for a map, the datatype value will not be 'image', but 'map'
	stmdata_object.image.attrs['datatype'] = stmdata_object.datatype
	stmdata_object.image.attrs['spectype'] = stmdata_object.spectype

	return stmdata_object
