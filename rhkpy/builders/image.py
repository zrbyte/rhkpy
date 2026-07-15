"""Construction of the `image` xarray Dataset (topography, current, lia).

Moved verbatim from rhkpy_loader.py (refactor phase 2).
"""

import numpy as np
import xarray as xr

from .detect import _get_filename


def _xr_image(stmdata_object):
	"""Create the `image` Dataset (topography, current, lia; forward/backward)
	of an image or map measurement, with coordinates in nm."""
	# topography
	topofw = stmdata_object.spymdata.Topography_Forward
	topobw = stmdata_object.spymdata.Topography_Backward
	
	# Load image data
	# use spym to align (flatten the data) and planefit
	# topofw, bg = align(topofw, baseline='median')
	# topobw, bg = align(topobw, baseline='median')
	# topofw, bg = plane(topofw)
	# topobw, bg = plane(topobw)

	# current
	currfw = stmdata_object.spymdata.Current_Forward
	currbw = stmdata_object.spymdata.Current_Backward
	# lia
	liafw = stmdata_object.spymdata.LIA_Current_Forward
	liabw = stmdata_object.spymdata.LIA_Current_Backward

	# The image data also needs to be flipped along the slow scan direction,
	# so that it shows up as the RHK Rev software would display it, when plotting with xarray.plot().
	# this behaviour is because xarray.plot, uses by default pcolormesh() to plot.
	# pcolormesh() flips the data along the slow scan direction. imshow() plots it the way it looks in RHK Rev and Gwyddion.
	topofw = np.flipud(topofw)
	topobw = np.flipud(topobw)
	currfw = np.flipud(currfw)
	currbw = np.flipud(currbw)
	liafw = np.flipud(liafw)
	liabw = np.flipud(liabw)

	# coordinates
	# absolute values should be found by adding the X Y offsets
	xoff = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Xoffset']
	yoff = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Yoffset']

	# these are the relative coordinates (from 0 to size of the image)
	xx = stmdata_object.spymdata.Topography_Forward_x.data
	yy = stmdata_object.spymdata.Topography_Forward_y.data

	# calculate the relative coordinates, including rotation
	# the offset refers to the corner of the image, so we need to account for that
	xlength = np.abs(xx[-1] - xx[0])
	ylength = np.abs(yy[-1] - yy[0])

	xoff -= xlength/2
	yoff -= ylength/2

	# create xarray Dataset of the image data
	xrimage = xr.Dataset(
		data_vars = dict(
			topography = (['y', 'x', 'scandir'], np.stack((topofw.data, topobw.data), axis=-1)*10**9),
			current = (['y', 'x', 'scandir'], np.stack((currfw.data, currbw.data), axis=-1)*10**12),
			lia = (['y', 'x', 'scandir'], np.stack((liafw.data, liabw.data), axis=-1)*10**12)
			),
		coords = dict(
			x = xx*10**9,
			y = yy*10**9,
			scandir = np.array(['forward', 'backward'])
			),
		attrs = dict(
			filename = _get_filename(stmdata_object.filename),
			xoffset = xoff*10**9,
			yoffset = yoff*10**9,
			xoffset_units = 'nm',
			yoffset_units = 'nm'
			)
		)

	# calculate image size
	pixelsizex = np.abs(xx[1] - xx[0])
	pixelsizey = np.abs(yy[1] - yy[0])
	xrimage.attrs['size_x'] = round((xlength + pixelsizex)*10**9, 3)
	xrimage.attrs['size_y'] = round((ylength + pixelsizey)*10**9, 3)
	xrimage.attrs['size_x units'] = 'nm'
	xrimage.attrs['size_y units'] = 'nm'

	xrimage['topography'].attrs['units'] = 'nm'
	xrimage['topography'].attrs['long units'] = 'nanometer'
	xrimage['lia'].attrs['units'] = 'pA'
	xrimage['lia'].attrs['long units'] = 'picoampere'
	xrimage['current'].attrs['units'] = 'pA'
	xrimage['current'].attrs['long units'] = 'picoampere'
	xrimage.coords['x'].attrs['units'] = 'nm'
	xrimage.coords['y'].attrs['units'] = 'nm'
	xrimage.coords['x'].attrs['long units'] = 'nanometer'
	xrimage.coords['y'].attrs['long units'] = 'nanometer'
	xrimage.coords['x'].attrs['note'] = 'fast scan direction\n'
	xrimage.coords['y'].attrs['note'] = 'slow scan direction\n'

	stmdata_object.image = xrimage
	return stmdata_object

def _xr_image_line(stmdata_object):
	"""Create the `image` Dataset of a line spectroscopy measurement, where the
	"image" is the repeated topography line scan."""
	# topography
	topofw = stmdata_object.spymdata.Topography_Forward
	topobw = stmdata_object.spymdata.Topography_Backward
	
	# current
	currfw = stmdata_object.spymdata.Current_Forward
	currbw = stmdata_object.spymdata.Current_Backward
	# lia
	liafw = stmdata_object.spymdata.LIA_Current_Forward
	liabw = stmdata_object.spymdata.LIA_Current_Backward

	# The image data also needs to be flipped along the slow scan direction,
	# so that it shows up as the RHK Rev software would display it, when plotting with xarray.plot().
	# this behaviour is because xarray.plot, uses by default pcolormesh() to plot.
	# pcolormesh() flips the data along the slow scan direction. imshow() plots it the way it looks in RHK Rev and Gwyddion.
	# topofw = np.flipud(topofw)
	# topobw = np.flipud(topobw)
	# currfw = np.flipud(currfw)
	# currbw = np.flipud(currbw)
	# liafw = np.flipud(liafw)
	# liabw = np.flipud(liabw)

	# coordinates
	# absolute values should be found by adding the X Y offsets
	xoff = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Xoffset']
	yoff = stmdata_object.spymdata.Topography_Forward.attrs['RHK_Yoffset']

	# these are the relative coordinates (from 0 to size of the image)
	xx = stmdata_object.spymdata.Topography_Forward_x.data
	yy = stmdata_object.spymdata.Topography_Forward_y.data

	# calculate the relative coordinates, including rotation
	# the offset refers to the corner of the image, so we need to account for that
	xlength = np.abs(xx[-1] - xx[0])
	ylength = np.abs(yy[-1] - yy[0])

	xoff -= xlength/2
	yoff -= ylength/2

	# create xarray Dataset of the image data
	xrimage = xr.Dataset(
		data_vars = dict(
			topography = (['y', 'x', 'scandir'], np.stack((topofw.data, topobw.data), axis=-1)*10**9),
			current = (['y', 'x', 'scandir'], np.stack((currfw.data, currbw.data), axis=-1)*10**12),
			lia = (['y', 'x', 'scandir'], np.stack((liafw.data, liabw.data), axis=-1)*10**12)
			),
		coords = dict(
			y = xx*10**9,
			x = yy*10**9,
			scandir = np.array(['forward', 'backward'])
			),
		attrs = dict(
			filename = _get_filename(stmdata_object.filename),
			xoffset = xoff*10**9,
			yoffset = yoff*10**9,
			xoffset_units = 'nm',
			yoffset_units = 'nm'
			)
		)

	xrimage['topography'].attrs['units'] = 'nm'
	xrimage['topography'].attrs['long units'] = 'nanometer'
	xrimage['lia'].attrs['units'] = 'pA'
	xrimage['lia'].attrs['long units'] = 'picoampere'
	xrimage['current'].attrs['units'] = 'pA'
	xrimage['current'].attrs['long units'] = 'picoampere'	
	xrimage.coords['x'].attrs['units'] = 'nm'
	xrimage.coords['x'].attrs['long units'] = 'nanometer'
	xrimage.coords['x'].attrs['note'] = 'fast scan direction\n'
	xrimage.coords['y'].attrs['units'] = None
	xrimage.coords['y'].attrs['note'] = 'repetitions of the topography line\n'
	

	stmdata_object.image = xrimage
	return stmdata_object
