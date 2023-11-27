"""Main WPLT module.

This module includes everything that an external user should use. It also acts
as an intermediary to the global figure by including all of its pass-through
functions as functions here. Therefore you can use this module as if it was
an instance of Figure.
"""

from .figure import Figure
from .global_figure import plot, save, preview, xrange, yrange, xaxis, yaxis, grid, legend, title
from .time_series import TimeSeries

# Setup internal logging.
import logging
logging.basicConfig(level=logging.WARN)
