"""Figure module.

Graphical figures for plotting numerical data. It can be both previewed in a popup 
window and saved into file. The main contents of the whole WPLT package is included 
inside the Figure class.
"""

import logging
from .output import convert_to_image, convert_to_video, preview_image, save_image, save_video
from .time_series import TimeSeries, TimeObjectAbstract
from collections.abc import Iterable

class Figure:
    """A class for plotting numerical data into graphical figures.

    Provides all the functionality needed to setup a graphical figure with plotted
    data, auxillary details such as a cartesian grid, and outputting that figure
    through the 'output' module.

    Attributes:
    - figsize: tuple[int, int]
        Sets the outputted size of the figure.
    """

    def __init__(self, figsize=(18, 14)):
        if not isinstance(figsize, tuple):
            raise TypeError("'figsize' must be a tuple with two integer.")
        
        if figsize[0] == 0 or figsize[1] == 0:
            raise ValueError("'figsize' cannot be set to size 0.")

        self.figsize = figsize
        
        self.plots = []
        self.c_plane = CartesianPlane()
        self.video = False
        self.use_legend = False
        self.title_text = None

    def plot(self, X, Y, scatter=False, label=None, width=1):
        """Plot data and add it onto the figure.

        Plotting data here will not instantly render a new graphical figure
        but instead setup and calculate everything needed to do so in the
        preview/save stage.

        Parameters:
        - X: np.array
            An array of x-coordinates.
        - Y: np.array
            An array of y-coordinates.
        - scatter: bool
            Whether or not to scatter data as points or draw them as lines.
        - label: string
            Labelling the plot. Displayed with '.legend()'.
        - width: int
            Width of line or diameter width of points.
        """
        if not isinstance(X, Iterable | TimeObjectAbstract):
            raise TypeError("'X' must be an iterable")
        
        if not isinstance(Y, Iterable | TimeObjectAbstract):
            raise TypeError("'Y' must be an iterable")

        if (isinstance(X, Iterable) and len(X) == 0) or (isinstance(Y, Iterable) and len(Y) == 0):
            raise ValueError("'X' and 'Y' must contain at least one value.")
        
        if isinstance(X, Iterable) and isinstance(Y, Iterable) and len(X) != len(Y):
            raise ValueError(f"Length of 'X' and 'Y' must match.")
        
        plot = None

        # Setup a new plot
        if TimeSeries.contains_time_series(X) or TimeSeries.contains_time_series(Y):
            plot = TimePlot(X, Y, label, width, scatter)
            self.video = True 
        else:
            plot = Plot(X, Y, label, width, scatter)

        logging.info(f"{'Scattering' if scatter else 'Plotting' } {plot} on {self}")

        # Pre-calculate plot values and cartesian plane
        plot.evaluate()
        self.c_plane.recalculate(plot)

        # Save plot for output.
        self.plots.append(plot) 

    def xrange(self, x_left, x_right):
        """Adjust range of x-axis.

        Pass-through to cartesian plane instance.
        
        Parameters:
        - x_left: int
            Leftmost value in x-axis.
        - x_right: int
            Rightmost value in x-axis.
        """
        self.c_plane.set_xrange(x_left, x_right)
    
    def yrange(self, y_bottom, y_top):
        """Adjust range of y-axis.

        Pass-through to cartesian plane instance.

        Parameters:
        - y_bottom: int
            Bottom value in y-axis.
        - x_right: int
            Top value in y-axis.
        """
        self.c_plane.set_yrange(y_bottom, y_top)

    def xaxis(self):
        """Display x-axis in render.
        
        Pass-through to cartesian plane instance.
        """
        self.c_plane.set_xaxis()
    
    def yaxis(self):
        """Display y-axis in render.
        
        Pass-through to cartesian plane instance.
        """
        self.c_plane.set_yaxis()
    
    def grid(self, x_steps=1, y_steps=1):
        """Display cartesian plane in render.

        A background grid. Pass-through to cartesian plane instance.
        """
        self.c_plane.set_grid(x_steps, y_steps)

    def legend(self):
        """Display legend at the top left of the figure. 
        
        This requires adding labels to one or more of theplots first.
        """
        if self.use_legend:
            logging.warn(f"Legend on figure {id(self)} is already activated.")

        self.use_legend = True

    def title(self, title_text):
        """Adds a title to the top of the figure.
        
        Paramters:
        - title_text: string
            Title to display at the of the figure.
        """
        if not isinstance(title_text, str):
            raise TypeError("'title_text' must be a string.")
        
        if len(title_text) == 0:
            raise ValueError("'title_text' cannot be empty.")

        if self.title_text is not None:
            logging.warn(f"Overriding previous title on figure {id(self)}.")

        self.title_text = title_text

    def preview(self):
        """Previews figure with plots added to it. 
        
        Not available for video (i.e. when using TimeSeries).
        """
        if not self.plots:
            raise Exception("No plots to preview.")

        if self.video:
            raise Exception("Preview not available on video.")
        
        logging.info(f"Previewing {self}")

        img = convert_to_image(self)
        preview_image(img)
    
    def save(self):
        """Saves figure with plots added to it.

        Writes both images and videos to PNG.
        """
        if not self.plots:
            raise Exception("No plots to preview.")

        logging.info(f"Saving {self}")

        if self.video:
            video = convert_to_video(self)
            save_video(video)
        else:
            img = convert_to_image(self)
            save_image(img)

class Plot:
    """A class for handling plotted data.

    Evaluates the plotted data, and stores information and settings
    regarding the plot.

    Attributes:
    - X: np.array
        An array of x-coordinates.
    - Y: np.array
        An array of y-coordinates.
    - scatter: bool
        Whether or not to scatter data as points or draw them as lines.
    - label: string
        Labelling the plot. Displayed with '.legend()'.
    - width: int
        Width of line or diameter width of points.
    """

    def __init__(self, X, Y, label, width, scatter=False):
        if not isinstance(X, Iterable | TimeObjectAbstract):
            raise TypeError("'X' must be an iterable")
        
        if not isinstance(Y, Iterable | TimeObjectAbstract):
            raise TypeError("'Y' must be an iterable")

        if (isinstance(X, Iterable) and len(X) == 0) or (isinstance(Y, Iterable) and len(Y) == 0):
            raise ValueError("'X' and 'Y' must contain at least one value.")
        
        if isinstance(X, Iterable) and isinstance(Y, Iterable) and len(X) != len(Y):
            raise ValueError(f"Length of 'X' and 'Y' must match.")
        
        self.X = X
        self.Y = Y
        self.label = label
        self.width = width
        self.scatter = scatter

        self.result = None
    
    def evaluate(self):
        """Calculate values in plot.

        Nothing special for the standard type of plot.
        """
        self.result = (self.X, self.Y)

    def __repr__(self):
        return f"{str(type(self))[8:-2]}({_repr_list(self.X)}, {_repr_list(self.Y)})"

class TimePlot(Plot):
    """A subclass of Plot used with TimeSeries.

    Evaluates the time-based plotted data, and stores information 
    and settings regarding the plot.
    """
    def __init__(self, X, Y, label, width, scatter=False):
        super().__init__(X, Y, label, width, scatter)
    
    def evaluate(self):
        """Calculate values in plot.

        Pre-calculates all possible values for the data based on
        time from 0 to 1. 'TIME_RANGE' constant in TimeSeries
        decides for how many different frames.
        """
        self.result = []
        for i in range(TimeSeries.TIME_RANGE):
            t = i / (TimeSeries.TIME_RANGE-1)
            
            X = TimeSeries.evaluate_total(self.X, t)
            Y = TimeSeries.evaluate_total(self.Y, t)
            self.result.append((X, Y))

class CartesianPlane:
    """A class for handling a figure's cartesian plane.

    Allows setting the figures breadth of visible coordinates, displaying
    details, and calculating coordinates.
    """

    X_TICKS = 10
    Y_TICKS = 8

    def __init__(self):
        # X-axis
        self.x_left = None
        self.x_right = None
        self.x_fixed = False

        # Y-axis
        self.y_bottom = None
        self.y_top = None
        self.y_fixed = False

        # Axies
        self.x_axis = False
        self.y_axis = False 
        
        # Grid
        self.grid = False
        self.grid_steps = None
    
    def recalculate(self, plot):
        """Recalculate boundaries.

        Adjusts the plane's boundaries to include the 
        newly added plot.

        Parameters:
        - plot: Plot
            newly added plot.
        """
        if not isinstance(plot, Plot):
            raise TypeError("'plot' must be of type 'Plot'.")

        if plot.result is None:
            raise Exception("Plot has not been evaluated.")

        def find_min_max(arr, prev_min, prev_max, is_fixed):
            """Find the min and max."""
            _min, _max = prev_min or arr[0], prev_max or arr[0]

            if not is_fixed:
                for item in arr:
                    _min = min(item, _min)
                    _max = max(item, _max)

            return _min, _max
        
        # Flatten out the result arrays into two 1-D arrays (for X and Y).
        values = plot.result if isinstance(plot, TimePlot) else [plot.result]
        X = [val for vals in values for val in vals[0]]
        Y = [val for vals in values for val in vals[1]]

        # Adjust boundaries.
        self.x_left, self.x_right = find_min_max(X, self.x_left, self.x_right, self.x_fixed)
        self.y_bottom, self.y_top = find_min_max(Y, self.y_bottom, self.y_top, self.y_fixed)

    def set_xrange(self, x_left, x_right):
        """Adjust range of x-axis.

        Parameters:
        - x_left: int
            Leftmost value in x-axis.
        - x_right: int
            Rightmost value in x-axis.
        """
        if not isinstance(x_left, int) or not isinstance(x_right, int):
            raise TypeError("'x_left' and 'x_right' must be integers.")
        
        if x_left == x_right:
            raise ValueError("'x_left' and 'x_right' cannot have the same value.")

        if self.x_fixed:
            logging.warn(f"Range of X has already been set for figure {id(self)}")

        self.x_left = x_left
        self.x_right = x_right
        self.x_fixed = True

    def set_yrange(self, y_bottom, y_top):
        """Adjust range of y-axis.

        Parameters:
        - y_bottom: int
            Bottom value in y-axis.
        - x_right: int
            Top value in y-axis.
        """
        if not isinstance(y_bottom, int) or not isinstance(y_top, int):
            raise TypeError("'y_bottom' and 'y_top' must be integers.")
        
        if y_bottom == y_top:
            raise ValueError("'y_bottom' and 'y_top' cannot have the same value.")
        
        if self.y_fixed:
            logging.warn(f"Range of Y has already been set for figure {id(self)}")

        self.y_bottom = y_bottom
        self.y_top = y_top
        self.y_fixed = True
    
    def set_xaxis(self):
        """Display x-axis in render."""
        if self.x_axis:
            logging.warn(f"X-axis on figure {id(self)} is already activated.")

        self.x_axis = True

    def set_yaxis(self):
        """Display y-axis in render."""
        if self.y_axis:
            logging.warn(f"Y-axis on figure {id(self)} is already activated.")

        self.y_axis = True

    def set_grid(self, x_steps, y_steps):
        """Display cartesian plane in render.

        A background grid.

        Parameters:
        - x_steps: int
            Vertical line separation.
        - y_steps: int
            Horizontal line separation.
        """
        if not isinstance(x_steps, int) or not isinstance(y_steps, int):
            raise TypeError("'x_steps' and 'y_steps' must be integers.")

        if x_steps == 0 or y_steps == 0:
            raise ValueError("'x_steps' and 'y_steps' cannot be set to 0.")

        if self.grid:
            logging.warn(f"Grid has already been set for figure {id(self)}.")

        self.grid = True
        self.grid_steps = (x_steps, y_steps)

    def get_xdelta(self):
        """Calculate width of x-axis."""
        return abs(self.x_right - self.x_left)

    def get_ydelta(self):
        """Calculate height of y-axis."""
        return abs(self.y_top - self.y_bottom)
    
    def normalize_coord(self, coord):
        """Normalize a coordinate to the boundaries.
        
        Parameters:
        - coord: tuple[int, int]
            Coordinate to normalize.

        Returns:
            Coordinate between (0,0) to (1,1).
        """
        if not isinstance(coord, tuple):
            raise TypeError("'coord' must be a tuple of two integers.")

        x = (coord[0] - self.x_left) / (self.x_right - self.x_left)
        y = (coord[1] - self.y_bottom) / (self.y_top - self.y_bottom)

        return (x, y)
    
    def _round_steps(self, num, start=10.0, decimals=-1):
        """Round a number to a clear and aesthetic value.
        
        Find the closest value to num by multiplying or dividing
        by factors 2 and 5 from a starting value 10.

        Will result in numbers such as ...0.5, 1.0, 2, 5...

        Parameters:
        - num: float
            Input number to be rounded towards.
        - start: float
            Starting number for estimation.
        - decimals: int
            Number of decimals in estimated number. Negative means
            that it is further from including a decimal.
        """
        def update_decimals(old, new):
            """Calculate latest decimal position."""
            nonlocal decimals

            # Determined the change in factors of ten, excluding rest
            old_cmp = old // (10**(-decimals))
            new_cmp = new // (10**(-decimals))

            # Compare change in relative to a
            if old_cmp > new_cmp:
                decimals += 1
            elif old_cmp < new_cmp:
                decimals -= 1 

        # Check for 0 case
        if num == 0:
            return 0, 0

        # Check for negative number
        if num < 0 and start > 0:
            start *= -1

        # Calculated factor based alternatives.
        alts = [start/5, start/2, start*2, start*5]
        
        # Find best alternative
        best_alt = start
        for alt in alts:
            if abs(alt - num) < abs(best_alt - num):
                best_alt = alt

        # Check if estimation has improved.
        if best_alt == start:
            return start, decimals
        else:
            # Continue estimation if it still has improved.
            update_decimals(start, best_alt)
            return self._round_steps(num, best_alt, decimals)

    def get_xsteps(self):
        """Generate rounded steps from 'x_left' to 'x_right'."""
        x_step, x_decimals = self._round_steps(self.get_xdelta() / self.X_TICKS) 
        x, _ = self._round_steps(self.x_left)

        while (x <= self.x_right):
            yield x
            x = round(x+x_step, x_decimals)

    def get_ysteps(self):
        """Generate rounded steps from 'y_bottom' to 'y_top'."""
        y_step, y_decimals = self._round_steps(self.get_ydelta() / self.Y_TICKS) 
        y, _ = self._round_steps(self.y_bottom)

        while (y <= self.y_top):
            yield y
            y = round(y+y_step, y_decimals)


def _repr_list(arr, maxlength=10):
    """Represent an array with string."""
    if TimeSeries.contains_time_series(arr):
        return "TimeSeries..."

    r_arr = ", ".join(repr(item) for item in arr)

    if len(r_arr) >= maxlength:
        r_arr = r_arr[:maxlength] + "..."

    return f"[{r_arr}]"
