"""Quick-plot internals for rhkdata instances.

These are the implementations behind :meth:`rhkpy.rhkdata.qplot` and the
``rhkdata._qplot_*`` methods. Bodies moved verbatim from the rhkdata class in
rhkpy_loader.py (refactor phase 2), with ``self`` renamed to ``rhkdata_obj``.
"""

import hvplot.xarray  # noqa: F401 - registers the .hvplot accessor
import panel as pn


def plot_topo(rhkdata_obj, cmap_topo = 'fire', **kwargs):
	"""Plotting topography data using :py:mod:`hvplot`.

	:param cmap_topo: colorscale used for topography data, defaults to 'fire'
	:type cmap_topo: str, optional

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	# The backward direction should be plotted, since this is the direction in which the tip moves, when the spectroscopy data is measured.
	return rhkdata_obj.image.topography[:, :, 1].hvplot.image(x = 'x', y = 'y', cmap = cmap_topo, title = 'topography backward', **kwargs)


def plot_lia(rhkdata_obj, cmap_spec = 'viridis', **kwargs):
	"""Plotting dI/dV image data using :py:mod:`hvplot`.

	:param cmap_spec: colorscale used for dI/dV data, defaults to 'viridis'
	:type cmap_spec: str, optional

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	return rhkdata_obj.image.lia[:, :, 1].hvplot.image(cmap = cmap_spec, x = 'x', y = 'y', title = 'dI/dV backward')


def plot_map_iv(rhkdata_obj, cmap_spec = 'viridis', **kwargs):
	"""Plotting dI/dV map data using :py:mod:`hvplot`.
	The mean values (biasscandir and repetitions) of the dI/dV signal are plotted on the density plot.

	:param cmap_spec: colorscale used for dI/dV data, defaults to 'viridis'
	:type cmap_spec: str, optional

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	# take the mean of the spectra in a point and plot it
	meanmap = rhkdata_obj.spectra.mean(dim = ['repetitions', 'biasscandir'])
	# select the lia
	specplot = meanmap.lia.hvplot.image(
		x = 'specpos_x',
		y = 'specpos_y',
		groupby = 'bias',
		cmap = cmap_spec,
		title = 'dI/dV map'
	)
	# holoviews plot
	return specplot


def plot_map_iz(rhkdata_obj, cmap_spec = 'viridis', **kwargs):
	"""Plotting I(z) map data using :py:mod:`hvplot`.

	:param cmap_spec: colorscale used for I(z) data, defaults to 'viridis'
	:type cmap_spec: str, optional

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	# take the mean of the spectra in a point and plot it
	meanmap = rhkdata_obj.spectra.mean(dim = ['repetitions', 'zscandir'])
	specplot = meanmap.current.hvplot.image(
		x = 'specpos_x',
		y = 'specpos_y',
		groupby = 'z',
		cmap = cmap_spec,
		title = 'I(z) map'
	)
	return specplot


def plot_line_iv(rhkdata_obj, cmap_spec = 'viridis', **kwargs):
	"""Plotting dI/dV line data on a density plot (bias vs distance), using :py:mod:`hvplot`.
	The mean values of the dI/dV signal are plotted on the density plot.

	:param cmap_spec: colorscale used for dI/dV data, defaults to 'viridis'
	:type cmap_spec: str, optional

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	# take the mean of the spectra in a point and plot it
	meanmap = rhkdata_obj.spectra.mean(dim = ['repetitions', 'biasscandir'])
	# select the lia
	specplot = meanmap.lia.hvplot.image(
		x = 'bias',
		y = 'dist',
		cmap = cmap_spec,
		title = 'dI/dV line spectra',
		aspect = 1
	)
	return specplot


def plot_line_spec_iv(rhkdata_obj, **kwargs):
	"""Plotting dI/dV spectra of a line spectroscopy instance, using :py:mod:`hvplot`.

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	# plot repetitions and biasscandir on the same plot
	# do the first plot, if there are more than 1 repetitions, plot the average first
	if len(rhkdata_obj.spectra.repetitions) == 1:
		lineplot_fw = rhkdata_obj.spectra.lia[:, :, 0, 0].hvplot.line(x = 'bias', color = 'red', label = 'left')
		lineplot_bw = rhkdata_obj.spectra.lia[:, :, 0, 1].hvplot.line(x = 'bias', color = 'blue', label = 'right')
	elif len(rhkdata_obj.spectra.repetitions) > 1:
		lineplot_fw = rhkdata_obj.spectra.lia[:, :, 0, 0].hvplot.line(x = 'bias', color = 'LightCoral', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		lineplot_bw = rhkdata_obj.spectra.lia[:, :, 0, 1].hvplot.line(x = 'bias', color = 'LightSkyBlue', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		for i in range(1, len(rhkdata_obj.spectra.repetitions)):
			# iterate through the repetitions and plot on the same plot
			lineplot_fw *= rhkdata_obj.spectra.lia[:, :, i, 0].hvplot.line(x = 'bias', color = 'LightCoral', line_dash = 'dotted', line_width = 0.5, alpha = 1)
			lineplot_bw *= rhkdata_obj.spectra.lia[:, :, i, 1].hvplot.line(x = 'bias', color = 'LightSkyBlue', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		lineplot_fw *= rhkdata_obj.spectra.lia.mean(dim = 'repetitions')[:, :, 0].hvplot.line(x = 'bias', color = 'red', line_width = 2, label = 'avg left')
		lineplot_bw *= rhkdata_obj.spectra.lia.mean(dim = 'repetitions')[:, :, 1].hvplot.line(x = 'bias', color = 'blue', line_width = 2, label = 'avg right')

	# combine the fw and bw bias sweeps
	return lineplot_fw * lineplot_bw


def plot_line_iz(rhkdata_obj, cmap_spec = 'viridis', **kwargs):
	"""Plotting I(z) line data on a density plot (tip height vs distance), using :py:mod:`hvplot`.
	The mean values of the I(z) signal are plotted.

	:param cmap_spec: colorscale used for dI/dV data, defaults to 'viridis'
	:type cmap_spec: str, optional

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	meanmap = rhkdata_obj.spectra.mean(dim = ['repetitions', 'zscandir'])
	# select the current
	specplot = meanmap.current.hvplot.image(
		x = 'z',
		y = 'dist',
		cmap = cmap_spec,
		title = 'I(z) line spectra',
		aspect = 1
	)
	return specplot


def plot_line_spec_iz(rhkdata_obj, **kwargs):
	"""Plotting I(z) spectra of a line spectroscopy instance, using :py:mod:`hvplot`.

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	# plot repetitions and zscandir on the same plot
	# if there are more repetitions, the first plot will be the average
	if len(rhkdata_obj.spectra.repetitions) == 1:
		lineplot_fw = rhkdata_obj.spectra.current[:, :, 0, 0].hvplot.line(x = 'z', color = 'red', label = 'up')
		lineplot_bw = rhkdata_obj.spectra.current[:, :, 0, 1].hvplot.line(x = 'z', color = 'blue', label = 'down')
	elif len(rhkdata_obj.spectra.repetitions) > 1:
		lineplot_fw = rhkdata_obj.spectra.current[:, :, 0, 0].hvplot.line(x = 'z', color = 'LightCoral', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		lineplot_bw = rhkdata_obj.spectra.current[:, :, 0, 1].hvplot.line(x = 'z', color = 'LightSkyBlue', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		for i in range(1, len(rhkdata_obj.spectra.repetitions)):
			# iterate through the repetitions and plot on the same plot
			lineplot_fw *= rhkdata_obj.spectra.current[:, :, i, 0].hvplot.line(x = 'z', color = 'LightCoral', line_dash = 'dotted', line_width = 0.5, alpha = 1)
			lineplot_bw *= rhkdata_obj.spectra.current[:, :, i, 1].hvplot.line(x = 'z', color = 'LightSkyBlue', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		lineplot_fw *= rhkdata_obj.spectra.current.mean(dim = 'repetitions')[:, :, 0].hvplot.line(x = 'z', color = 'red', line_width = 2, label = 'avg up')
		lineplot_bw *= rhkdata_obj.spectra.current.mean(dim = 'repetitions')[:, :, 1].hvplot.line(x = 'z', color = 'blue', line_width = 2, label = 'avg down')

	# combine the fw and bw z sweeps
	return lineplot_fw * lineplot_bw


def plot_spec_iv_lia(rhkdata_obj, **kwargs):
	"""Plotting the dI/dV signal of a single spectrum instance, using :py:mod:`hvplot`.

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	if len(rhkdata_obj.spectra.repetitions) == 1:
		liaplot_fw = rhkdata_obj.spectra.lia[:, 0, 0].hvplot.line(x = 'bias', color = 'red', label = 'left')
		liaplot_bw = rhkdata_obj.spectra.lia[:, 0, 1].hvplot.line(x = 'bias', color = 'blue', label = 'right')
	elif len(rhkdata_obj.spectra.repetitions) > 1:
		liaplot_fw = rhkdata_obj.spectra.lia[:, 0, 0].hvplot.line(x = 'bias', color = 'LightCoral', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		liaplot_bw = rhkdata_obj.spectra.lia[:, 0, 1].hvplot.line(x = 'bias', color = 'LightSkyBlue', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		for i in range(1, len(rhkdata_obj.spectra.repetitions)):
			# iterate through the repetitions and plot on the same plot
			liaplot_fw *= rhkdata_obj.spectra.lia[:, i, 0].hvplot.line(x = 'bias', color = 'LightCoral', line_dash = 'dotted', line_width = 0.5, alpha = 1)
			liaplot_bw *= rhkdata_obj.spectra.lia[:, i, 1].hvplot.line(x = 'bias', color = 'LightSkyBlue', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		liaplot_fw *= rhkdata_obj.spectra.lia.mean(dim = 'repetitions')[:, 0].hvplot.line(x = 'bias', color = 'red', line_width = 2, label = 'avg left')
		liaplot_bw *= rhkdata_obj.spectra.lia.mean(dim = 'repetitions')[:, 1].hvplot.line(x = 'bias', color = 'blue', line_width = 2, label = 'avg right')
	return (liaplot_fw*liaplot_bw).opts(width = 400, title = 'dI/dV')


def plot_spec_iv_curr(rhkdata_obj, **kwargs):
	"""Plotting the current signal of a single spectrum instance, using :py:mod:`hvplot`.

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	if len(rhkdata_obj.spectra.repetitions) == 1:
		currplot_fw = rhkdata_obj.spectra.current[:, 0, 0].hvplot.line(x = 'bias', color = 'red', label = 'left')
		currplot_bw = rhkdata_obj.spectra.current[:, 0, 1].hvplot.line(x = 'bias', color = 'blue', label = 'right')
	elif len(rhkdata_obj.spectra.repetitions) > 1:
		currplot_fw = rhkdata_obj.spectra.current[:, 0, 0].hvplot.line(x = 'bias', color = 'LightCoral', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		currplot_bw = rhkdata_obj.spectra.current[:, 0, 1].hvplot.line(x = 'bias', color = 'LightSkyBlue', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		for i in range(1, len(rhkdata_obj.spectra.repetitions)):
			# iterate through the repetitions and plot on the same plot
			currplot_fw *= rhkdata_obj.spectra.current[:, i, 0].hvplot.line(x = 'bias', color = 'LightCoral', line_dash = 'dotted', line_width = 0.5, alpha = 1)
			currplot_bw *= rhkdata_obj.spectra.current[:, i, 1].hvplot.line(x = 'bias', color = 'LightSkyBlue', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		currplot_fw *= rhkdata_obj.spectra.current.mean(dim = 'repetitions')[:, 0].hvplot.line(x = 'bias', color = 'red', line_width = 2, label = 'avg left')
		currplot_bw *= rhkdata_obj.spectra.current.mean(dim = 'repetitions')[:, 1].hvplot.line(x = 'bias', color = 'blue', line_width = 2, label = 'avg right')
	return (currplot_fw*currplot_bw).opts(width = 400, title = 'current')


def plot_spec_iz(rhkdata_obj, **kwargs):
	"""Plotting an I(z) single spectrum instance, using :py:mod:`hvplot`.

	:return: :py:mod:`holoviews` plot
	:rtype: :py:mod:`holoviews`
	"""
	if len(rhkdata_obj.spectra.repetitions) == 1:
		specplot_up = rhkdata_obj.spectra.current[:, 0, 0].hvplot.line(x = 'z', color = 'red', label = 'up')
		specplot_down = rhkdata_obj.spectra.current[:, 0, 1].hvplot.line(x = 'z', color = 'blue', label = 'down')
	elif len(rhkdata_obj.spectra.repetitions) > 1:
		specplot_up = rhkdata_obj.spectra.current[:, 0, 0].hvplot.line(x = 'z', color = 'LightCoral', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		specplot_down = rhkdata_obj.spectra.current[:, 0, 1].hvplot.line(x = 'z', color = 'LightSkyBlue', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		for i in range(1, len(rhkdata_obj.spectra.repetitions)):
			# iterate through the repetitions and plot on the same plot
			specplot_up *= rhkdata_obj.spectra.current[:, i, 0].hvplot.line(x = 'z', color = 'LightCoral', line_dash = 'dotted', line_width = 0.5, alpha = 1)
			specplot_down *= rhkdata_obj.spectra.current[:, i, 1].hvplot.line(x = 'z', color = 'LightSkyBlue', line_dash = 'dotted', line_width = 0.5, alpha = 1)
		specplot_up *= rhkdata_obj.spectra.current.mean(dim = 'repetitions')[:, 0].hvplot.line(x = 'z', color = 'red', line_width = 2, label = 'avg up')
		specplot_down *= rhkdata_obj.spectra.current.mean(dim = 'repetitions')[:, 1].hvplot.line(x = 'z', color = 'blue', line_width = 2, label = 'avg down')
	return specplot_up*specplot_down


def qplot(rhkdata_obj, width = None, **kwargs):
	"""Quick plot of an :class:`~rhkpy.rhkpy_loader.rhkdata` instance.
	See :meth:`rhkpy.rhkpy_loader.rhkdata.qplot` for the documented interface.
	"""
	if rhkdata_obj.datatype == 'image':
		topo_plot = plot_topo(rhkdata_obj, **kwargs)
		lia_plot = plot_lia(rhkdata_obj, **kwargs)
		final_plot = pn.Row(pn.panel(topo_plot), pn.panel(lia_plot))
	elif rhkdata_obj.datatype == 'map':
		# if the rhkdata instance is 'map'
		if rhkdata_obj.spectype == 'iv':
			specplot = plot_map_iv(rhkdata_obj, **kwargs)
		elif rhkdata_obj.spectype == 'iz':
			specplot = plot_map_iz(rhkdata_obj, **kwargs)
		# plot the topography
		topoplot = plot_topo(rhkdata_obj, **kwargs)
		# adjust options
		topoplot.opts(frame_width = width)
		specplot.opts(frame_width = width)
		# separate the plots and the widget into panels, so I can place the widget
		topo_static = pn.panel(topoplot)
		spec_dynamic = pn.panel(specplot)
		# extract the widget
		widget_panel = spec_dynamic[0]
		specplot_static = spec_dynamic[1]
		# combined plot
		final_plot = pn.Row(topo_static, pn.Column(widget_panel, specplot_static))
	elif rhkdata_obj.datatype == 'line':
		if rhkdata_obj.spectype == 'iv':
			specplot = plot_line_iv(rhkdata_obj, **kwargs)
			# plot a selected spectrum along the dist dimensions
			combined = plot_line_spec_iv(rhkdata_obj, **kwargs)
			# if width parameter is specified, set the size of the plots
			if width is None:
				twod_plot_panel = pn.panel(specplot)
				combined_panel = pn.panel(combined)
			else:
				twod_plot_panel = pn.panel(specplot.opts(frame_width = int(0.8*width)))
				combined_panel = pn.panel(combined.opts(frame_width = width))
			# separate the widget and plot into panels
			plot_panel = combined_panel[0]
			plot_widget = combined_panel[1]
			# combined plot
			final_plot = pn.Row(twod_plot_panel, pn.Column(plot_widget, plot_panel))
		elif rhkdata_obj.spectype == 'iz':
			# take the mean of the spectra in a point and plot it
			specplot = plot_line_iz(rhkdata_obj, **kwargs)
			combined = plot_line_spec_iz(rhkdata_obj, **kwargs)
			# if width parameter is specified, set the size of the plots
			if width is None:
				twod_plot_panel = pn.panel(specplot)
				combined_panel = pn.panel(combined)
			else:
				twod_plot_panel = pn.panel(specplot.opts(frame_width = int(0.8*width)))
				combined_panel = pn.panel(combined.opts(frame_width = width))
			# separate the widget and plot into panels
			plot_panel = combined_panel[0]
			plot_widget = combined_panel[1]
			# combined plot
			final_plot = pn.Row(twod_plot_panel, pn.Column(plot_widget, plot_panel))

	elif rhkdata_obj.datatype == 'spec':
		if rhkdata_obj.spectype == 'iv':
			leftpanel = plot_spec_iv_lia(rhkdata_obj, **kwargs)
			rightpanel = plot_spec_iv_curr(rhkdata_obj, **kwargs)
			left_panel = pn.panel(leftpanel)
			right_panel = pn.panel(rightpanel)
			final_plot = pn.Row(left_panel, right_panel)
		elif rhkdata_obj.spectype == 'iz':
			combined = plot_spec_iz(rhkdata_obj, **kwargs)
			final_plot = pn.panel(combined.opts(width = 400, title = 'current'))

	return final_plot
