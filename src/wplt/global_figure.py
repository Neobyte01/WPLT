from .figure import Figure

global_fig = Figure()

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
