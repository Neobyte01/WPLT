import logging
from .output import convert_to_image, convert_to_video, preview_image, save_image, save_video
from .time_series import TimeSeries
from collections.abc import Iterable
import numpy as np

class Figure:
    def __init__(self, figsize=(18, 14)):
        self.figsize = figsize
        self.plots = []
        self.c_plane = CartesianPlane()
        self.video = False
        self.use_legend = False
        self.title_text = None

    def plot(self, X, Y, scatter=False, label=None, width=1):
        plot = None

        if TimeSeries.contains_time_series(X) or TimeSeries.contains_time_series(Y):
            plot = TimePlot(X, Y, label, width, scatter)
            self.video = True 
        else:
            plot = Plot(X, Y, label, width, scatter)

        plot.evaluate()
        self.c_plane.recalculate(plot)

        self.plots.append(plot) 

        logging.info(f"{'Scattering' if scatter else 'Plotting' } {self.plots[-1]} on {self}")

    def xrange(self, x_left, x_right):
        self.c_plane.set_xrange(x_left, x_right)
    
    def yrange(self, y_bottom, y_top):
        self.c_plane.set_yrange(y_bottom, y_top)

    def xaxis(self):
        self.c_plane.set_xaxis()
    
    def yaxis(self):
        self.c_plane.set_yaxis()
    
    def grid(self, x_steps=1, y_steps=1):
        self.c_plane.set_grid(x_steps, y_steps)

    def legend(self):
        self.use_legend = True

    def title(self, title_text):
        self.title_text = title_text

    def preview(self):
        if self.video:
            raise Exception("Preview not available on video.")
        
        logging.info(f"Previewing {self}")

        img = convert_to_image(self)
        preview_image(img)
    
    def save(self):
        logging.info(f"Saving {self}")

        if self.video:
            video = convert_to_video(self)
            save_video(video)
        else:
            img = convert_to_image(self)
            save_image(img)

class Plot:
    def __init__(self, X, Y, label, width, scatter=False):
        self.X = X
        self.Y = Y
        self.label = label
        self.width = width
        self.scatter = scatter
        self.result = None
    
    def evaluate(self):
        self.result = (self.X, self.Y)

    def __repr__(self):
        return f"{str(type(self))[8:-2]}({_repr_list(self.X)}, {_repr_list(self.Y)})"

class TimePlot(Plot):
    def __init__(self, X, Y, label, width, scatter=False):
        super().__init__(X, Y, label, width, scatter)
    
    def evaluate(self):
        self.result = []
        for i in range(TimeSeries.TIME_RANGE):
            t = i / (TimeSeries.TIME_RANGE-1)
            
            X = TimeSeries.evaluate_total(self.X, t)
            Y = TimeSeries.evaluate_total(self.Y, t)
            self.result.append((X, Y))

class CartesianPlane:
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
        def find_min_max(arr, prev_min, prev_max, is_fixed):
            _min, _max = prev_min or arr[0], prev_max or arr[0]

            if not is_fixed:
                for item in arr:
                    _min = min(item, _min)
                    _max = max(item, _max)

            return _min, _max
        
        values = plot.result if isinstance(plot, TimePlot) else [plot.result]
        X = [val for vals in values for val in vals[0]]
        Y = [val for vals in values for val in vals[1]]

        self.x_left, self.x_right = find_min_max(X, self.x_left, self.x_right, self.x_fixed)
        self.y_bottom, self.y_top = find_min_max(Y, self.y_bottom, self.y_top, self.y_fixed)

    def set_xrange(self, x_left, x_right):
        self.x_left = x_left
        self.x_right = x_right
        self.x_fixed = True

    def set_yrange(self, y_bottom, y_top):
        self.y_bottom = y_bottom
        self.y_top = y_top
        self.y_fixed = True
    
    def set_xaxis(self):
        self.x_axis = True

    def set_yaxis(self):
        self.y_axis = True

    def set_grid(self, x_steps, y_steps):
        self.grid = True
        self.grid_steps = (x_steps, y_steps)

    def get_xdelta(self):
        return abs(self.x_right - self.x_left)

    def get_ydelta(self):
        return abs(self.y_top - self.y_bottom)
    
    def normalize_coord(self, coord):
        x = (coord[0] - self.x_left) / (self.x_right - self.x_left)
        y = (coord[1] - self.y_bottom) / (self.y_top - self.y_bottom)

        return (x, y)
    
    def _round_steps(self, num, start=10, decimals=-1):
        def update_decimals(old, new):
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

        alts = [start/5, start/2, start*2, start*5]
        
        best_alt = start
        for alt in alts:
            if abs(alt - num) < abs(best_alt - num):
                best_alt = alt

        if best_alt == start:
            return start, decimals
        else:
            update_decimals(start, best_alt)
            return self._round_steps(num, best_alt, decimals)

    def get_xsteps(self):
        x_step, x_decimals = self._round_steps(self.get_xdelta() / self.X_TICKS) 
        x, _ = self._round_steps(self.x_left)

        while (x <= self.x_right):
            yield x
            x = round(x+x_step, x_decimals)

    def get_ysteps(self):
        y_step, y_decimals = self._round_steps(self.get_ydelta() / self.Y_TICKS) 
        y, _ = self._round_steps(self.y_bottom)

        while (y <= self.y_top):
            yield y
            y = round(y+y_step, y_decimals)


def _repr_list(arr, maxlength=10):
    if TimeSeries.contains_time_series(arr):
        return "TimeSeries..."

    r_arr = ", ".join(repr(item) for item in arr)

    if len(r_arr) >= maxlength:
        r_arr = r_arr[:maxlength] + "..."

    return f"[{r_arr}]"
