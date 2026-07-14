"""Backward-compatibility shim (refactor phase 2).

The implementation now lives in:

- :mod:`rhkpy.analysis` - fitting, background subtraction, Dataset operations
- :mod:`rhkpy.plotting` - navigation plot, thumbnail generation

This module re-exports the public (and historical) names so that existing
imports like ``from rhkpy.rhkpy_process import peakfit`` keep working
unchanged.
"""

# historical module-level imports, kept because they are part of the public
# namespace of this module (and of rhkpy itself, via the star import)
import matplotlib.pyplot as pl
import numpy as np
import xarray as xr
import copy, glob, re, os
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from scipy import ndimage
import hvplot.xarray
import holoviews as hv

from .analysis.fitting import gaussian, lorentz, gaussian2, polynomial_fit, bgsubtract, peakfit
from .analysis.ops import coord_to_absolute, polyflatten, mapsection
from .plotting.navigation import navigation
from .plotting.thumbnails import genthumbs, _setup_webdriver
