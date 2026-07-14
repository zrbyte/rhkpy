"""Analysis functions: curve fitting, background subtraction, and operations
on rhkdata xarray Datasets."""

from .fitting import gaussian, lorentz, gaussian2, polynomial_fit, bgsubtract, peakfit
from .ops import coord_to_absolute, polyflatten, mapsection
