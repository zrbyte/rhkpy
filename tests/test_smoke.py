"""Smoke tests: exercise the public entry points end-to-end on the real
fixture data and on small synthetic datasets. These do not pin numerical
output (the characterization tests do that); they verify that the public
functions run without raising and return the expected kind of object.
"""

import shutil

import numpy as np
import pytest
import xarray as xr

from conftest import TESTDATA_DIR, sm4_fixture_names


def _first(loaded_fixtures, datatype, spectype=None):
	"""First successfully loaded fixture with the given datatype/spectype."""
	for name, (status, data) in loaded_fixtures.items():
		if status != 'ok':
			continue
		if data.datatype == datatype and (spectype is None or data.spectype == spectype):
			return data
	pytest.skip(f'no loadable fixture with datatype={datatype} spectype={spectype}')


# ---------------------------------------------------------------- plotting

@pytest.mark.parametrize('sm4name', sm4_fixture_names())
def test_qplot(sm4name, loaded_fixtures):
	status, data = loaded_fixtures[sm4name]
	if status != 'ok':
		pytest.skip(f'{sm4name} does not load (characterized separately)')
	plot = data.qplot()
	assert plot is not None


def test_navigation(loaded_fixtures):
	import rhkpy
	topo = _first(loaded_fixtures, 'image')
	specmap = _first(loaded_fixtures, 'map', 'iv')
	plot = rhkpy.navigation(topo, specmap)
	assert plot is not None


@pytest.mark.slow
def test_genthumbs(loaded_fixtures, tmp_path):
	"""End-to-end thumbnail generation (starts a headless browser - slow)."""
	import rhkpy
	# two small fixtures that are known to load
	for name in ['Iz_Stripes-9K-HOPG-SPI2-3_2021_09_07_10_15_28_529.sm4',
			'dI-dV_Stripes-9K-HOPG-SPI2-3_2021_09_07_10_23_58_152.sm4']:
		src = TESTDATA_DIR / name
		if src.is_file():
			shutil.copy(src, tmp_path / name)
	copied = list(tmp_path.glob('*.sm4'))
	assert copied, 'no fixture files available to copy'
	rhkpy.genthumbs(str(tmp_path))
	pngs = list(tmp_path.glob('*.png'))
	assert len(pngs) == len(copied)


# ------------------------------------------------------------ rhkdata methods

def test_coord_to_absolute(loaded_fixtures):
	specmap = _first(loaded_fixtures, 'map')
	absolute = specmap.coord_to_absolute()
	assert absolute is not specmap
	assert absolute.datatype == specmap.datatype


def test_polyflatten(loaded_fixtures):
	image = _first(loaded_fixtures, 'image')
	flattened = image.polyflatten()
	assert flattened is not image
	assert 'topography' in flattened.image


def test_print_info(loaded_fixtures, capsys):
	data = _first(loaded_fixtures, 'map')
	data.print_info()
	assert capsys.readouterr().out.strip()


# ------------------------------------------------------------------ analysis

def test_mapsection(loaded_fixtures):
	import rhkpy
	specmap = _first(loaded_fixtures, 'map', 'iv')
	x = specmap.spectra.specpos_x.values
	y = specmap.spectra.specpos_y.values
	section = rhkpy.mapsection(specmap.spectra, (x.min(), y.min()), (x.max(), y.max()))
	assert 'dist' in section.dims


def test_bgsubtract_synthetic():
	import rhkpy
	x = np.linspace(-10, 10, 500)
	y = rhkpy.gaussian(x, x0=0, ampl=5, width=0.5) + 0.1 * x + 1
	result = rhkpy.bgsubtract(x, y)
	y_nobg = result[0]
	assert y_nobg.shape == y.shape
	# background (offset + slope) should be mostly removed far from the peak
	assert abs(np.mean(y_nobg[:50])) < 0.5


def test_peakfit_synthetic():
	import rhkpy
	bias = np.linspace(-1, 1, 200)
	da = xr.DataArray(
		rhkpy.gaussian(bias, x0=0.1, ampl=2, width=0.3),
		coords={'bias': bias}, dims=['bias'],
	)
	fit = rhkpy.peakfit(da, stval={'x0': 0.0, 'ampl': 1.5, 'width': 0.2})
	assert 'curvefit_coefficients' in fit
	x0_fitted = float(fit.curvefit_coefficients.sel(param='x0'))
	assert abs(x0_fitted - 0.1) < 0.01


def test_fit_functions_evaluate():
	import rhkpy
	x = np.linspace(-5, 5, 11)
	assert rhkpy.gaussian(x).shape == x.shape
	assert rhkpy.lorentz(x).shape == x.shape
	assert rhkpy.gaussian2(x).shape == x.shape
	coeffs, covar = rhkpy.polynomial_fit(2, x, x ** 2)
	assert len(coeffs) == 3
	assert covar.shape == (3, 3)
