"""Global figure module.

Contains the global figure that is available directly 
via 'wplt'. There is a special exception in the pass-through
functions, '.preview()' and '.save()' causes the global figure
to reset to ensure safety.

Example:
    wplt.plot(X, Y)
    wplt.preview()
"""

from .figure import Figure

global_fig = Figure()

# -- Pass-through functions --

def plot(*args, **kwargs):
    global_fig.plot(*args, **kwargs)

def xrange(*args):
    global_fig.xrange(*args)    

def yrange(*args):
    global_fig.yrange(*args)    

def xaxis():
    global_fig.xaxis()

def yaxis():
    global_fig.yaxis()

def grid(*args):
    global_fig.grid(*args)

def legend():
    global_fig.legend()

def title(*args):
    global_fig.title(*args)

def preview(**kwargs):
    global_fig.preview(**kwargs)
    global_fig.plots = []

def save(**kwargs):
    global_fig.save(**kwargs)
    global_fig.plots = []
