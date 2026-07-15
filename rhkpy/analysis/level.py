"""Image leveling: row alignment and plane subtraction.

Ported verbatim from the spym project by Mirco Panighel
(https://github.com/rescipy-project/spym, MIT license). These functions are
part of the historical public rhkpy namespace (``rhkpy.align``,
``rhkpy.plane``).
"""

import numpy as np


def plane(image):
    '''Corrects for image tilting by subtraction of a plane.

    :param image: image data
    :type image: 2D :py:mod:`numpy` array

    :return: flattened image ``planned`` and the subtracted background ``bkg``
    :rtype: tuple: (2D :py:mod:`numpy` array, 2D :py:mod:`numpy` array)

    :Example:

        .. code-block:: python

            import rhkpy

            topo = rhkpy.rhkdata('topography.sm4', loadraw = True)
            # plane-fit the forward scan of the raw topography
            flattened, background = rhkpy.plane(topo.image.topography.sel(scandir = 'forward').data)
    '''

    bkg_x = _poly_bkg(image.mean(axis=0), 1)
    bkg_y = _poly_bkg(image.mean(axis=1), 1)

    bkg_xx = np.apply_along_axis(_fill, 1, image, bkg_x)
    bkg_yy = np.apply_along_axis(_fill, 0, image, bkg_y)

    bkg = bkg_xx + bkg_yy
    planned = image - bkg

    return planned, bkg


def align(image, baseline='mean', axis=1, poly_degree=2):
    '''Align the rows (scan lines) of an image by subtracting a baseline from each.

    :param image: image data
    :type image: 2D :py:mod:`numpy` array
    :param baseline: how the baselines are estimated: 'mean', 'median' or 'poly', defaults to 'mean'
    :type baseline: str, optional
    :param axis: axis along which the baselines are calculated, defaults to 1
    :type axis: int, optional
    :param poly_degree: polynomial degree if ``baseline`` = 'poly', defaults to 2
    :type poly_degree: int, optional

    :return: corrected image ``aligned`` and the subtracted background ``bkg``
    :rtype: tuple: (2D :py:mod:`numpy` array, 2D :py:mod:`numpy` array)
    '''

    if baseline == 'mean':
        bkg = np.apply_along_axis(_mean_bkg, axis, image)
    elif baseline == 'median':
        bkg = np.apply_along_axis(_median_bkg, axis, image)
    elif baseline == 'poly':
        bkg = np.apply_along_axis(_poly_bkg, axis, image, poly_degree)

    aligned = image - bkg

    return aligned, bkg


def _mean_bkg(line):
    return np.full(line.shape[0], line.mean())


def _median_bkg(line):
    return np.full(line.shape[0], np.median(line))


def _poly_bkg(line, poly_degree):
    x = np.linspace(-.5, .5, line.shape[0])
    coefs = np.polyfit(x, line, poly_degree)
    return np.polyval(coefs, x)


def _fill(line, value):
    return value
