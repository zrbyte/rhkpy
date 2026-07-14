"""Construction of the `spectra` xarray Dataset for each (datatype, spectype).

Moved verbatim from rhkpy_loader.py (refactor phase 2).
"""

import numpy as np
import xarray as xr

from .detect import _get_filename


def _xr_map_iv(stmdata_object):
	"""
	TODO need to change spectrum rearranging for the case where alternate is False

	Create a DataSet containing the Lock-In (LIA) and Current spectroscopy data
	Use the absolute values of the tip positions as coordinates

	In spym the spectroscopy data is loaded into an array,
	which has axis=0 the number of datapoints in the spectra
	and axis=1 the number of spectra in total.

	When rearranging, the number of repetitions within each tip position is assumed to be 1
	and alternate scan direction is assumed to be turned on.
	These options can be changed by the parameters, `repetitions` and `alternate`
	"""

	# extract the numpy array containing the LIA data from the spym object
	specarray = stmdata_object.spymdata.LIA_Current.data
	# extract the numpy array containing the Current data from the spym object
	currentarray = stmdata_object.spymdata.Current.data

	# total number of spectra in one postion of the tip
	numberofspectra = (stmdata_object.alternate + 1)*stmdata_object.repetitions
	# size of the map in mapsize x mapsize
	mapsize = int(np.sqrt(specarray.shape[1] / numberofspectra))

	# reshape LIA data
	# collect all spectra measured in the same `X, Y` coordinate into an axis (last) of an array.
	temp = np.reshape(specarray, (specarray.shape[0], -1, numberofspectra), order='C')
	# Every other spectrum is a forward and backward scan in bias sweep. Separate the forward and backward scans into differing arrays by slicing.
	# These are all the forward and backward bias sweep spectra, arranged along axis=1, with axis=2 being the repetitions
	spec_fw = temp[:, :, 0::2]
	spec_bw = temp[:, :, 1::2]
	# reshape the forward and backward parts into a map
	speccmap_fw = np.reshape(spec_fw, (spec_fw.shape[0], mapsize, mapsize, spec_fw.shape[2]), order='C')
	speccmap_bw = np.reshape(spec_bw, (spec_bw.shape[0], mapsize, mapsize, spec_bw.shape[2]), order='C')
	
	# The last axis (in this case with length of 1) contains the repeated scans in one particular pixel.
	# If the `repetitions` variable is set to greater than 1, this will contains the repeated spectra within an `X, Y` pixel.

	# need to flip the x and y axes so that the spectra line up with the topography image.
	# Meaning the first topo pixel in both directions is also the first spectroscopy pixel in each direction.
	liafw = np.flip(speccmap_fw, axis=(1, 2))
	liabw = np.flip(speccmap_bw, axis=(1, 2))

	# reshape Current data
	temp = np.reshape(currentarray, (currentarray.shape[0], -1, numberofspectra), order='C')
	# Every other spectrum is a forward and backward scan in bias sweep. Separate the forward and backward scans into differing arrays by slicing.
	# These are all the forward and backward bias sweep spectra, arranged along axis=1, with axis=2 being the repetitions
	current_fw = temp[:, :, 0::2]
	current_bw = temp[:, :, 1::2]
	# reshape the forward and backward parts into a map
	currentmap_fw = np.reshape(current_fw, (current_fw.shape[0], mapsize, mapsize, current_fw.shape[2]), order='C')
	currentmap_bw = np.reshape(current_bw, (current_bw.shape[0], mapsize, mapsize, current_bw.shape[2]), order='C')
	
	# The last axis (in this case with length of 1) contains the repeated scans in one particular pixel.
	# If the `repetitions` variable is set to greater than 1, this will contains the repeated spectra within an `X, Y` pixel.

	# need to flip the x and y axes so that the spectra line up with the topography image.
	# Meaning the first topo pixel in both directions is also the first spectroscopy pixel in each direction.
	currentfw = np.flip(currentmap_fw, axis=(1, 2))
	currentbw = np.flip(currentmap_bw, axis=(1, 2))

	# Coordinates of the spectroscopy map
	
	# 'RHK_SpecDrift_Xcoord' are the coordinates of the spectra.
	# This contains the coordinates in the order that the spectra are in. 
	xcoo = np.array(stmdata_object.spymdata.LIA_Current.attrs['RHK_SpecDrift_Xcoord'])
	ycoo = np.array(stmdata_object.spymdata.LIA_Current.attrs['RHK_SpecDrift_Ycoord'])
	
	# reshaping the spectra positions similarly to the spectra.
	meshx = np.reshape(xcoo, (mapsize, mapsize, numberofspectra), order='C')[:, :, 0]
	meshy = np.reshape(ycoo, (mapsize, mapsize, numberofspectra), order='C')[:, :, 0]
	
	# make coordinates for the spectra positions
	# calculate the pixel size, distance between the neighboring spectra
	pixelsizex = stmdata_object.image.attrs['size_x'] / mapsize
	pixelsizey = stmdata_object.image.attrs['size_y'] / mapsize
	# make coordinates for the spectra positions
	tempx = np.linspace(pixelsizex/2, stmdata_object.image.attrs['size_x'] - pixelsizex/2, num=mapsize) + stmdata_object.image.attrs['xoffset']
	tempy = np.linspace(pixelsizey/2, stmdata_object.image.attrs['size_y'] - pixelsizey/2, num=mapsize) + stmdata_object.image.attrs['yoffset']

	# Constructing the xarray DataSet 
	# stacking the forward and backward bias sweeps and using the scandir coordinate
	# also adding specific attributes
	xrspec = xr.Dataset(
		data_vars = dict(
			lia = (['bias', 'specpos_y', 'specpos_x', 'repetitions', 'biasscandir'], np.stack((liafw, liabw), axis=-1)*10**12),
			current = (['bias', 'specpos_y', 'specpos_x', 'repetitions', 'biasscandir'], np.stack((currentfw, currentbw), axis=-1)*10**12),
			x = (['specpos_y', 'specpos_x'], meshx*10**9),
			y = (['specpos_y', 'specpos_x'], meshy*10**9)
			),
		coords = dict(
			bias = stmdata_object.spymdata.coords['LIA_Current_x'].data,
			specpos_x = tempx,
			specpos_y = tempy,
			repetitions = np.array(range(stmdata_object.repetitions)),
			biasscandir = np.array(['left', 'right'], dtype = 'U')
			),
		attrs = dict(filename = _get_filename(stmdata_object.filename))
	)

	xrspec['lia'].attrs['units'] = 'pA'
	xrspec['lia'].attrs['long units'] = 'picoampere'
	xrspec['current'].attrs['units'] = 'pA'
	xrspec['current'].attrs['long units'] = 'picoampere'
	xrspec['x'].attrs['units'] = 'nm'
	xrspec['x'].attrs['long units'] = 'nanometer'
	xrspec['y'].attrs['units'] = 'nm'
	xrspec['y'].attrs['long units'] = 'nanometer'
	xrspec.coords['bias'].attrs['units'] = 'V'
	xrspec.coords['bias'].attrs['long units'] = 'Volt'
	xrspec.coords['specpos_x'].attrs['units'] = 'nm'
	xrspec.coords['specpos_y'].attrs['units'] = 'nm'
	xrspec.coords['specpos_x'].attrs['long units'] = 'nanometer'
	xrspec.coords['specpos_y'].attrs['long units'] = 'nanometer'

	stmdata_object.spectra = xrspec
	return stmdata_object

def _xr_line_iv(stmdata_object):
	"""
	Create a DataSet containing the Lock-In (LIA) and Current spectroscopy data
	Use the absolute values of the tip positions as coordinates

	In spym the spectroscopy data is loaded into an array,
	which has axis=0 the number of datapoints in the spectra
	and axis=1 the number of spectra in total.

	When rearranging, the number of repetitions within each tip position is assumed to be 1
	and alternate scan direction is assumed to be turned on.
	These options can be changed by the parameters, `repetitions` and `alternate`
	"""

	# extract the numpy array containing the LIA data from the spym object
	specarray = stmdata_object.spymdata.LIA_Current.data
	# extract the numpy array containing the Current data from the spym object
	currentarray = stmdata_object.spymdata.Current.data

	# total number of spectra in one postion of the tip
	numberofspectra = int((stmdata_object.alternate + 1)*stmdata_object.repetitions)
	# size of the line, the number of the different physical positions of the tip
	linesize = int(specarray.shape[1] / numberofspectra)

	# reshape LIA data
	# Every other spectrum is a forward and backward scan in bias sweep. Separate the forward and backward scans into differing arrays by slicing.
	# These are all the forward and backward bias sweep spectra, arranged along axis=1, with axis=2 being the repetitions
	templia = np.reshape(specarray, (specarray.shape[0], -1, numberofspectra), order='C')
	liafw = templia[:, :, 0::2]
	liabw = templia[:, :, 1::2]

	# reshape Current data
	tempcurr = np.reshape(currentarray, (currentarray.shape[0], -1, numberofspectra), order='C')
	currentfw = tempcurr[:, :, 0::2]
	currentbw = tempcurr[:, :, 1::2]

	# Coordinates of the spectroscopy map
	# 'RHK_SpecDrift_Xcoord' are the coordinates of the spectra.
	# This contains the coordinates in the order that the spectra are in. 
	xcoo = np.array(stmdata_object.spymdata.LIA_Current.attrs['RHK_SpecDrift_Xcoord'])
	ycoo = np.array(stmdata_object.spymdata.LIA_Current.attrs['RHK_SpecDrift_Ycoord'])
	# reshaping the coordinates similarly to the spectra. Need only every nth coordinate, where n is then number of spectra in a tip position
	tempx = xcoo[0::numberofspectra]
	tempy = ycoo[0::numberofspectra]
	linelength = np.sqrt((tempx[-1] - tempx[0])**2 + (tempy[-1] - tempy[0])**2)
	# distance coordinates along the line in [nm]
	linecoord = np.linspace(0, linelength, num=tempx.shape[0])*10**9

	"""
	Constructing the xarray Dataset 
	"""
	# stacking the forward and backward bias sweeps and using the scandir coordinate
	# also adding specific attributes
	xrspec = xr.Dataset(
		data_vars = dict(
			lia = (['bias', 'dist', 'repetitions', 'biasscandir'], np.stack((liafw, liabw), axis=-1)*10**12),
			current = (['bias', 'dist', 'repetitions', 'biasscandir'], np.stack((currentfw, currentbw), axis=-1)*10**12),
			x = (['dist'], tempx*10**9),
			y = (['dist'], tempy*10**9)
			),
		coords = dict(
			bias = stmdata_object.spymdata.coords['LIA_Current_x'].data,
			dist = linecoord,
			repetitions = np.array(range(stmdata_object.repetitions)),
			biasscandir = np.array(['left', 'right'], dtype = 'U')
			),
		attrs = dict(filename = _get_filename(stmdata_object.filename))
	)

	xrspec.coords['dist'].attrs['units'] = 'nm'
	xrspec.coords['dist'].attrs['long units'] = 'nanometer'
	xrspec.coords['bias'].attrs['units'] = 'V'
	xrspec.coords['bias'].attrs['long units'] = 'Volt'

	xrspec['x'].attrs['units'] = 'nm'
	xrspec['y'].attrs['units'] = 'nm'
	xrspec['x'].attrs['long units'] = 'nanometer'
	xrspec['y'].attrs['long units'] = 'nanometer'
	xrspec['lia'].attrs['units'] = 'pA'
	xrspec['lia'].attrs['long units'] = 'picoampere'
	xrspec['current'].attrs['units'] = 'pA'
	xrspec['current'].attrs['long units'] = 'picoampere'

	stmdata_object.spectra = xrspec
	return stmdata_object

def _xr_spec_iv(stmdata_object):
	"""
	Create a DataSet containing the Lock-In (LIA) and Current spectroscopy data
	Use the absolute values of the tip positions are in the attributes
	"""

	# extract the numpy array containing the LIA data from the spym object
	specarray = stmdata_object.spymdata.LIA_Current.data
	# extract the numpy array containing the Current data from the spym object
	currentarray = stmdata_object.spymdata.Current.data

	# reshape LIA data
	# Every other spectrum is a forward and backward scan in bias sweep. Separate the forward and backward scans into differing arrays by slicing.
	liafw = specarray[:, 0::2]
	liabw = specarray[:, 1::2]

	# reshape Current data
	currentfw = currentarray[:, 0::2]
	currentbw = currentarray[:, 1::2]

	# Coordinates of the spectroscopy map
	# 'RHK_SpecDrift_Xcoord' are the coordinates of the spectra.
	# This contains the coordinates in the order that the spectra are in. 
	# Here we only need the first x and y components
	xcoo = np.array(stmdata_object.spymdata.LIA_Current.attrs['RHK_SpecDrift_Xcoord'])
	ycoo = np.array(stmdata_object.spymdata.LIA_Current.attrs['RHK_SpecDrift_Ycoord'])
	# reshaping the coordinates similarly to the spectra.
	tempx = xcoo[0]
	tempy = ycoo[0]

	# Constructing the xarray Dataset 
	# stacking the forward and backward bias sweeps and using the scandir coordinate
	# also adding specific attributes
	xrspec = xr.Dataset(
		data_vars = dict(
			lia = (['bias', 'repetitions', 'biasscandir'], np.stack((liafw, liabw), axis=-1)*10**12),
			current = (['bias', 'repetitions', 'biasscandir'], np.stack((currentfw, currentbw), axis=-1)*10**12),
			x = tempx*10**9,
			y = tempy*10**9
			),
		coords = dict(
			bias = stmdata_object.spymdata.coords['LIA_Current_x'].data,
			repetitions = np.array(range(stmdata_object.repetitions)),
			biasscandir = np.array(['left', 'right'], dtype = 'U')
			),
		attrs = dict(filename = _get_filename(stmdata_object.filename))
	)

	xrspec.coords['bias'].attrs['units'] = 'V'
	xrspec.coords['bias'].attrs['long units'] = 'Volt'

	xrspec.attrs['speccoord_x'] = tempx*10**9
	xrspec.attrs['speccoord_y'] = tempy*10**9
	xrspec.attrs['speccoord_x units'] = 'nm'
	xrspec.attrs['speccoord_y units'] = 'nm'

	xrspec['x'].attrs['units'] = 'nm'
	xrspec['y'].attrs['units'] = 'nm'
	xrspec['x'].attrs['long units'] = 'nanometer'
	xrspec['y'].attrs['long units'] = 'nanometer'
	xrspec['lia'].attrs['units'] = 'pA'
	xrspec['lia'].attrs['long units'] = 'picoampere'
	xrspec['current'].attrs['units'] = 'pA'
	xrspec['current'].attrs['long units'] = 'picoampere'

	stmdata_object.spectra = xrspec
	return stmdata_object

def _xr_map_iz(stmdata_object):
	"""
	TODO need to change spectrum rearranging for the case where alternate is False

	Create a DataSet containing the Lock-In (LIA) and Current spectroscopy data
	Use the absolute values of the tip positions as coordinates

	In spym the spectroscopy data is loaded into an array,
	which has axis=0 the number of datapoints in the spectra
	and axis=1 the number of spectra in total.

	When rearranging, the number of repetitions within each tip position is assumed to be 1
	and alternate scan direction is assumed to be turned on.
	These options can be changed by the parameters, `repetitions` and `alternate`
	"""

	# extract the numpy array containing the Current data from the spym object
	currentarray = stmdata_object.spymdata.Current.data

	# total number of spectra in one postion of the tip
	numberofspectra = (stmdata_object.alternate + 1)*stmdata_object.repetitions
	# size of the map in mapsize x mapsize
	mapsize = int(np.sqrt(currentarray.shape[1] / numberofspectra))

	# reshape Current data
	temp = np.reshape(currentarray, (currentarray.shape[0], -1, numberofspectra), order='C')
	# Every other spectrum is a forward and backward scan in bias sweep. Separate the forward and backward scans into differing arrays by slicing.
	# These are all the forward and backward bias sweep spectra, arranged along axis=1, with axis=2 being the repetitions
	current_fw = temp[:, :, 0::2]
	current_bw = temp[:, :, 1::2]
	# reshape the forward and backward parts into a map
	currentmap_fw = np.reshape(current_fw, (current_fw.shape[0], mapsize, mapsize, current_fw.shape[2]), order='C')
	currentmap_bw = np.reshape(current_bw, (current_bw.shape[0], mapsize, mapsize, current_bw.shape[2]), order='C')
	"""
	The last axis (in this case with length of 1) contains the repeated scans in one particular pixel.
	If the `repetitions` variable is set to greater than 1, this will contains the repeated spectra within an `X, Y` pixel.
	"""
	currentfw = np.flip(currentmap_fw, axis=(1, 2))
	currentbw = np.flip(currentmap_bw, axis=(1, 2))

	"""
	Coordinates of the spectroscopy map
	"""
	# 'RHK_SpecDrift_Xcoord' are the coordinates of the spectra.
	# This contains the coordinates in the order that the spectra are in. 
	xcoo = np.array(stmdata_object.spymdata.Current.attrs['RHK_SpecDrift_Xcoord'])
	ycoo = np.array(stmdata_object.spymdata.Current.attrs['RHK_SpecDrift_Ycoord'])
	# reshaping the spectra positions similarly to the spectra.
	meshx = np.reshape(xcoo, (mapsize, mapsize, numberofspectra), order='C')[:, :, 0]
	meshy = np.reshape(ycoo, (mapsize, mapsize, numberofspectra), order='C')[:, :, 0]
	
	# make coordinates for the spectra positions
	# calculate the pixel size, distance between the neighboring spectra
	pixelsizex = stmdata_object.image.attrs['size_x'] / mapsize
	pixelsizey = stmdata_object.image.attrs['size_y'] / mapsize
	# make coordinates for the spectra positions
	tempx = np.linspace(pixelsizex/2, stmdata_object.image.attrs['size_x'] - pixelsizex/2, num=mapsize) + stmdata_object.image.attrs['xoffset']
	tempy = np.linspace(pixelsizey/2, stmdata_object.image.attrs['size_y'] - pixelsizey/2, num=mapsize) + stmdata_object.image.attrs['yoffset']

	"""
	Constructing the xarray DataSet 
	"""
	# stacking the forward and backward bias sweeps and using the scandir coordinate
	# also adding specific attributes
	xrspec = xr.Dataset(
		data_vars = dict(
			current = (['z', 'specpos_x', 'specpos_y', 'repetitions', 'zscandir'], np.stack((currentfw, currentbw), axis=-1)*10**12),
			x = (['specpos_x', 'specpos_y'], meshx*10**9),
			y = (['specpos_x', 'specpos_y'], meshy*10**9)
			),
		coords = dict(
			z = stmdata_object.spymdata.coords['Current_x'].data*10**9,
			specpos_x = tempx,
			specpos_y = tempy,
			repetitions = np.array(range(stmdata_object.repetitions)),
			zscandir = np.array(['up', 'down'], dtype = 'U')
			),
		attrs = dict(filename = _get_filename(stmdata_object.filename))
	)

	xrspec['current'].attrs['units'] = 'pA'
	xrspec['current'].attrs['long units'] = 'picoampere'
	xrspec['x'].attrs['units'] = 'nm'
	xrspec['x'].attrs['long units'] = 'nanometer'
	xrspec['y'].attrs['units'] = 'nm'
	xrspec['y'].attrs['long units'] = 'nanometer'
	xrspec.coords['z'].attrs['units'] = 'nm'
	xrspec.coords['z'].attrs['long units'] = 'nanometer'
	xrspec.coords['specpos_x'].attrs['units'] = 'nm'
	xrspec.coords['specpos_y'].attrs['units'] = 'nm'
	xrspec.coords['specpos_x'].attrs['long units'] = 'nanometer'
	xrspec.coords['specpos_y'].attrs['long units'] = 'nanometer'

	stmdata_object.spectra = xrspec
	return stmdata_object

def _xr_line_iz(stmdata_object):
	"""
	Create a DataSet containing the Lock-In (LIA) and Current spectroscopy data
	Use the absolute values of the tip positions as coordinates

	In spym the spectroscopy data is loaded into an array,
	which has axis=0 the number of datapoints in the spectra
	and axis=1 the number of spectra in total.

	When rearranging, the number of repetitions within each tip position is assumed to be 1
	and alternate scan direction is assumed to be turned on.
	These options can be changed by the parameters, `repetitions` and `alternate`
	"""

	# extract the numpy array containing the Current data from the spym object
	currentarray = stmdata_object.spymdata.Current.data

	# total number of spectra in one postion of the tip
	numberofspectra = int((stmdata_object.alternate + 1)*stmdata_object.repetitions)
	# size of the line, the number of the different physical positions of the tip
	linesize = int(currentarray.shape[1] / numberofspectra)

	# reshape Current data
	tempcurr = np.reshape(currentarray, (currentarray.shape[0], -1, numberofspectra), order='C')
	currentfw = tempcurr[:, :, 0::2]
	currentbw = tempcurr[:, :, 1::2]

	"""
	Coordinates of the spectroscopy map
	"""
	# 'RHK_SpecDrift_Xcoord' are the coordinates of the spectra.
	# This contains the coordinates in the order that the spectra are in. 
	xcoo = np.array(stmdata_object.spymdata.Current.attrs['RHK_SpecDrift_Xcoord'])
	ycoo = np.array(stmdata_object.spymdata.Current.attrs['RHK_SpecDrift_Ycoord'])
	# reshaping the coordinates similarly to the spectra. Need only every nth coordinate, where n is the number of spectra in a position
	tempx = xcoo[0::numberofspectra]
	tempy = ycoo[0::numberofspectra]
	linelength = np.sqrt((tempx[-1] - tempx[0])**2 + (tempy[-1] - tempy[0])**2)
	# distance coordinates along the line in [nm]
	linecoord = np.linspace(0, linelength, num=tempx.shape[0])*10**9

	"""
	Constructing the xarray Dataset 
	"""
	# stacking the forward and backward bias sweeps and using the scandir coordinate
	# also adding specific attributes
	xrspec = xr.Dataset(
		data_vars = dict(
			current = (['z', 'dist', 'repetitions', 'zscandir'], np.stack((currentfw, currentbw), axis=-1)*10**12),
			x = (['dist'], tempx*10**9),
			y = (['dist'], tempy*10**9)
			),
		coords = dict(
			z = stmdata_object.spymdata.coords['Current_x'].data*10**9,
			dist = linecoord,
			repetitions = np.array(range(stmdata_object.repetitions)),
			zscandir = np.array(['up', 'down'], dtype = 'U')
			),
		attrs = dict(filename = _get_filename(stmdata_object.filename))
	)

	xrspec.coords['dist'].attrs['units'] = 'nm'
	xrspec.coords['dist'].attrs['long units'] = 'nanometer'
	xrspec.coords['z'].attrs['units'] = 'nm'
	xrspec.coords['z'].attrs['long units'] = 'nanometer'

	xrspec['x'].attrs['units'] = 'nm'
	xrspec['y'].attrs['units'] = 'nm'
	xrspec['x'].attrs['long units'] = 'nanometer'
	xrspec['y'].attrs['long units'] = 'nanometer'
	xrspec['current'].attrs['units'] = 'pA'
	xrspec['current'].attrs['long units'] = 'picoampere'

	stmdata_object.spectra = xrspec
	return stmdata_object

def _xr_spec_iz(stmdata_object):
	"""
	Create a DataSet containing the Lock-In (LIA) and Current spectroscopy data
	Use the absolute values of the tip positions are in the attributes
	"""

	# extract the numpy array containing the Current data from the spym object
	currentarray = stmdata_object.spymdata.Current.data

	# reshape Current data
	currentfw = currentarray[:, 0::2]
	currentbw = currentarray[:, 1::2]

	"""
	Coordinates of the spectroscopy map
	"""
	# 'RHK_SpecDrift_Xcoord' are the coordinates of the spectra.
	# This contains the coordinates in the order that the spectra are in. 
	# Here we only need the first x and y components
	xcoo = np.array(stmdata_object.spymdata.Current.attrs['RHK_SpecDrift_Xcoord'])
	ycoo = np.array(stmdata_object.spymdata.Current.attrs['RHK_SpecDrift_Ycoord'])
	# reshaping the coordinates similarly to the spectra.
	tempx = xcoo[0]
	tempy = ycoo[0]

	"""
	Constructing the xarray Dataset 
	"""
	# stacking the forward and backward bias sweeps and using the scandir coordinate
	# also adding specific attributes
	xrspec = xr.Dataset(
		data_vars = dict(
			current = (['z', 'repetitions', 'zscandir'], np.stack((currentfw, currentbw), axis=-1)*10**12),
			x = tempx*10**9,
			y = tempy*10**9
			),
		coords = dict(
			z = stmdata_object.spymdata.coords['Current_x'].data*10**9,
			repetitions = np.array(range(stmdata_object.repetitions)),
			zscandir = np.array(['up', 'down'], dtype = 'U')
			),
		attrs = dict(filename = _get_filename(stmdata_object.filename))
	)

	xrspec['x'].attrs['units'] = 'nm'
	xrspec['y'].attrs['units'] = 'nm'
	xrspec['x'].attrs['long units'] = 'nanometer'
	xrspec['y'].attrs['long units'] = 'nanometer'
	xrspec.attrs['speccoord_x'] = tempx*10**9
	xrspec.attrs['speccoord_y'] = tempy*10**9
	xrspec.attrs['speccoord_x units'] = 'nm'
	xrspec.attrs['speccoord_y units'] = 'nm'
	xrspec.coords['z'].attrs['units'] = 'nm'
	xrspec.coords['z'].attrs['long units'] = 'nanometer'
	xrspec['current'].attrs['units'] = 'pA'
	xrspec['current'].attrs['long units'] = 'picoampere'

	stmdata_object.spectra = xrspec
	return stmdata_object
