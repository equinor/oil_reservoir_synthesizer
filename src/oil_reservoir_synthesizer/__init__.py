"""
This package generates synthetic oil simulator data based
on perlin noise. See :py:class:`OilSimulator`.
"""
from importlib.metadata import version
from ._oil_simulator import OilSimulator

__author__ = """Equinor"""
__email__ = "fg_sib-scout@equinor.com"

__version__ = version(__name__)

__all__ = [
    "OilSimulator",
]
