"""Attach measurement metadata (bias, setpoint, lock-in settings, ...) to the
constructed xarray Datasets.

Moved verbatim from rhkpy_loader.py (refactor phase 2).
"""


def _add_map_metadata(stmdata_object):
	if stmdata_object.spectype == 'iv':
		stmdata_object.spectra['lia'].attrs['bias'] = stmdata_object.spymdata.Current.attrs['bias']
		stmdata_object.spectra['lia'].attrs['bias units'] = 'V'
		stmdata_object.spectra['lia'].attrs['setpoint'] = stmdata_object.spymdata.Current.attrs['RHK_Current']*10**12
		stmdata_object.spectra['lia'].attrs['setpoint units'] = 'pA'
		stmdata_object.spectra['lia'].attrs['time_per_point'] = stmdata_object.spymdata.Current.attrs['time_per_point']

	stmdata_object.spectra['current'].attrs['bias'] = stmdata_object.spymdata.Current.attrs['bias']
	stmdata_object.spectra['current'].attrs['bias units'] = 'V'
	stmdata_object.spectra['current'].attrs['setpoint'] = stmdata_object.spymdata.Current.attrs['RHK_Current']*10**12
	stmdata_object.spectra['current'].attrs['setpoint units'] = 'pA'
	stmdata_object.spectra['current'].attrs['time_per_point'] = stmdata_object.spymdata.Current.attrs['time_per_point']
	stmdata_object.spectra.attrs['bias'] = stmdata_object.spymdata.Current.attrs['bias']
	stmdata_object.spectra.attrs['bias units'] = 'V'
	stmdata_object.spectra.attrs['setpoint'] = stmdata_object.spymdata.Current.attrs['RHK_Current']*10**12
	stmdata_object.spectra.attrs['setpoint units'] = 'pA'
	stmdata_object.spectra.attrs['measurement date'] = stmdata_object.spymdata.Current.attrs['RHK_Date']
	stmdata_object.spectra.attrs['measurement time'] = stmdata_object.spymdata.Current.attrs['RHK_Time']
	stmdata_object.spectra.attrs['scan angle'] = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Angle']
	stmdata_object.spectra.attrs['LI amplitude'] = stmdata_object.spymdata.Current.attrs['RHK_CH1Drive_Amplitude']*10**3
	stmdata_object.spectra.attrs['LI amplitude unit'] = 'mV'
	stmdata_object.spectra.attrs['LI frequency'] = stmdata_object.spymdata.Current.attrs['RHK_CH1Drive_Frequency']
	stmdata_object.spectra.attrs['LI frequency unit'] = 'Hz'
	stmdata_object.spectra.attrs['LI phase'] = stmdata_object.spymdata.Current.attrs['RHK_Lockin0_PhaseOffset']

	# store the data and spectrum type in the attributes
	stmdata_object.spectra.attrs['datatype'] = stmdata_object.datatype
	stmdata_object.spectra.attrs['spectype'] = stmdata_object.spectype

	return stmdata_object

def _add_line_metadata(stmdata_object):
	if stmdata_object.spectype == 'iv':
		stmdata_object.spectra['lia'].attrs['bias'] = stmdata_object.spymdata.Current.attrs['bias']
		stmdata_object.spectra['lia'].attrs['bias units'] = 'V'
		stmdata_object.spectra['lia'].attrs['setpoint'] = stmdata_object.spymdata.Current.attrs['RHK_Current']*10**12
		stmdata_object.spectra['lia'].attrs['setpoint units'] = 'pA'
		stmdata_object.spectra['lia'].attrs['time_per_point'] = stmdata_object.spymdata.Current.attrs['time_per_point']

	stmdata_object.spectra['current'].attrs['bias'] = stmdata_object.spymdata.Current.attrs['bias']
	stmdata_object.spectra['current'].attrs['bias units'] = 'V'
	stmdata_object.spectra['current'].attrs['setpoint'] = stmdata_object.spymdata.Current.attrs['RHK_Current']*10**12
	stmdata_object.spectra['current'].attrs['setpoint units'] = 'pA'
	stmdata_object.spectra['current'].attrs['time_per_point'] = stmdata_object.spymdata.Current.attrs['time_per_point']
	stmdata_object.spectra.attrs['bias'] = stmdata_object.spymdata.Current.attrs['bias']
	stmdata_object.spectra.attrs['bias units'] = 'V'
	stmdata_object.spectra.attrs['setpoint'] = stmdata_object.spymdata.Current.attrs['RHK_Current']*10**12
	stmdata_object.spectra.attrs['setpoint units'] = 'pA'
	stmdata_object.spectra.attrs['measurement date'] = stmdata_object.spymdata.Current.attrs['RHK_Date']
	stmdata_object.spectra.attrs['measurement time'] = stmdata_object.spymdata.Current.attrs['RHK_Time']
	stmdata_object.spectra.attrs['scan angle'] = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Angle']
	stmdata_object.spectra.attrs['LI amplitude'] = stmdata_object.spymdata.Current.attrs['RHK_CH1Drive_Amplitude']*10**3
	stmdata_object.spectra.attrs['LI amplitude unit'] = 'mV'
	stmdata_object.spectra.attrs['LI frequency'] = stmdata_object.spymdata.Current.attrs['RHK_CH1Drive_Frequency']
	stmdata_object.spectra.attrs['LI frequency unit'] = 'Hz'
	stmdata_object.spectra.attrs['LI phase'] = stmdata_object.spymdata.Current.attrs['RHK_Lockin0_PhaseOffset']

	# store the data and spectrum type in the attributes
	stmdata_object.spectra.attrs['datatype'] = stmdata_object.datatype
	stmdata_object.spectra.attrs['spectype'] = stmdata_object.spectype

	return stmdata_object

def _add_spec_metadata(stmdata_object):
	if stmdata_object.spectype == 'iv':
		stmdata_object.spectra['lia'].attrs['bias'] = stmdata_object.spymdata.Current.attrs['bias']
		stmdata_object.spectra['lia'].attrs['bias units'] = 'V'
		stmdata_object.spectra['lia'].attrs['setpoint'] = stmdata_object.spymdata.Current.attrs['RHK_Current']*10**12
		stmdata_object.spectra['lia'].attrs['setpoint units'] = 'pA'
		stmdata_object.spectra['lia'].attrs['time_per_point'] = stmdata_object.spymdata.Current.attrs['time_per_point']
		stmdata_object.spectra.coords['bias'].attrs['units'] = 'V'
		stmdata_object.spectra.coords['bias'].attrs['long units'] = 'volt'
	
	stmdata_object.spectra['current'].attrs['bias'] = stmdata_object.spymdata.Current.attrs['bias']
	stmdata_object.spectra['current'].attrs['bias units'] = 'V'
	stmdata_object.spectra['current'].attrs['setpoint'] = stmdata_object.spymdata.Current.attrs['RHK_Current']*10**12
	stmdata_object.spectra['current'].attrs['setpoint units'] = 'pA'
	stmdata_object.spectra['current'].attrs['time_per_point'] = stmdata_object.spymdata.Current.attrs['time_per_point']

	stmdata_object.spectra.attrs['bias'] = stmdata_object.spymdata.Current.attrs['bias']
	stmdata_object.spectra.attrs['bias units'] = 'V'
	stmdata_object.spectra.attrs['setpoint'] = stmdata_object.spymdata.Current.attrs['RHK_Current']*10**12
	stmdata_object.spectra.attrs['setpoint units'] = 'pA'
	stmdata_object.spectra.attrs['measurement date'] = stmdata_object.spymdata.Current.attrs['RHK_Date']
	stmdata_object.spectra.attrs['measurement time'] = stmdata_object.spymdata.Current.attrs['RHK_Time']
	stmdata_object.spectra.attrs['LI amplitude'] = stmdata_object.spymdata.Current.attrs['RHK_CH1Drive_Amplitude']*10**3
	stmdata_object.spectra.attrs['LI amplitude unit'] = 'mV'
	stmdata_object.spectra.attrs['LI frequency'] = stmdata_object.spymdata.Current.attrs['RHK_CH1Drive_Frequency']
	stmdata_object.spectra.attrs['LI frequency unit'] = 'Hz'
	stmdata_object.spectra.attrs['LI phase'] = stmdata_object.spymdata.Current.attrs['RHK_Lockin0_PhaseOffset']
	
	# store the data and spectrum type in the attributes
	stmdata_object.spectra.attrs['datatype'] = stmdata_object.datatype
	stmdata_object.spectra.attrs['spectype'] = stmdata_object.spectype
	
	return stmdata_object

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
