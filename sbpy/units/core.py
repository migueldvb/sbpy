# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
sbpy units core module
"""

__all__ = [
    'spectral_density_vega',
    'VEGAMAG'
]

import warnings
import numpy as np
import astropy.units as u
from astropy.utils.exceptions import AstropyWarning

try:
    from synphot.units import VEGAMAG
except ImportError:
    VEGAMAG = None

from ..spectroscopy.vega import Vega


def spectral_density_vega(wfb):
    """Flux density equivalencies with VEGAMAG.

    Uses the default `sbpy` Vega spectrum.

    Vega is assumed to have an apparent magnitude of 0 in the VEGAMAG
    system (``VEGAMAG``).  Note this is different from the
    Johnson-Morgan system, in which Vega has a magnitude of 0.03
    [Joh66, BM12]_.


    Parameters
    ----------
    wfb : `~astropy.units.Quantity`, `~synphot.SpectralElement`, string
        Wavelength, frequency, or a bandpass of the corresponding flux
        density being converted.  See
        :func:`~synphot.SpectralElement.from_filter()` for possible
        bandpass names.


    Returns
    -------
    eqv : list
        List of equivalencies.


    Examples
    --------
    >>> import astropy.units as u
    >>> from sbpy.units import spectral_density_vega, VEGAMAG
    >>> m = 0 * VEGAMAG
    >>> fluxd = m.to(u.Jy, spectral_density_vega(5500 * u.AA))
    >>> fluxd.value   # doctest: +FLOAT_CMP
    3679.226291142341


    References
    ----------
    [Joh66] Johnson et al. 1966, Commun. Lunar Planet. Lab. 4, 99

    [BM12] Bessell & Murphy 2012, PASP 124, 140-157

    """

    try:
        import synphot
    except ImportError:
        raise ImportError('synphot required for Vega-based magnitude'
                          ' conversions.')

    vega = Vega.from_default()
    if isinstance(wfb, u.Quantity):
        wav = wfb
        fnu0 = vega(wfb, unit='W/(m2 Hz)')
        flam0 = vega(wfb, unit='W/(m2 um)')
    elif isinstance(wfb, (synphot.SpectralElement, str)):
        fnu0 = vega.filt(wfb, unit='W/(m2 Hz)')[1]
        flam0 = vega.filt(wfb, unit='W/(m2 um)')[1]

    def forward(fluxd_vega):
        """nan/inf are returned as -99 mag.

        nan/inf handling consistent with
        :func:`~synphot.units.spectral_density_vega`.

        """
        def f(fluxd):
            m = -2.5 * np.log10(fluxd / fluxd_vega.value)
            m = np.ma.MaskedArray(m, mask=~np.isfinite(m)).filled(-99)
            if np.ndim(m) == 0:
                m = float(m)
            return m
        return f

    def backward(fluxd_vega):
        def b(m):
            return fluxd_vega.value * 10**(-0.4 * m)
        return b

    return [
        (fnu0.unit, VEGAMAG, forward(fnu0), backward(fnu0)),
        (flam0.unit, VEGAMAG, forward(flam0), backward(flam0)),
    ]
