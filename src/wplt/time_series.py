"""Time series module.

Time-based variables that allows plots to be animated. Supports basic
arithmetic operations, and can be used in functions with 'TimeSeries.apply(...)'.
"""

import numpy as np
from collections.abc import Iterable

class TimeObjectAbstract:
    """Abstract base class of all Time based objects.
    
    Contains all functionality that is required by objects
    inside this module. Even though the static methods can be
    used directly from this class, it is recommended to instead
    use the child class TimeSeries instead, outside of this module.
    """

    TIME_RANGE = 100  # Range of time for animations.

    def evaluate(self, t):
        """Evaluate object based on time parameter 't'."""
        raise NotImplementedError()
    
    @staticmethod
    def evaluate_ext(ext, t):
        """Evaluate external object based on time parameter 't'.
        
        Encapsulates more safety handling to handle unknown external types
        of input.
        """
        if isinstance(ext, TimeObjectAbstract):
            return ext.evaluate(t)
        elif isinstance(ext, Iterable):
            return np.asarray([TimeSeries.evaluate_ext(item, t) for item in ext], dtype=float)
        else:
            return ext
        
    @staticmethod
    def evaluate_total(obj, t):
        """Total recursive evaluation of an object.
        
        Final result would be a number or list of numbers, based
        on the recursive evaluations of children.
        """
        if isinstance(obj, Iterable):
            return np.array([TimeSeries.evaluate_ext(item, t) for item in obj])
        else:
            return TimeSeries.evaluate_ext(obj, t)

    @staticmethod
    def contains_time_series(obj):
        """Does an object contain a 'TimeSeries'."""
        if isinstance(obj, Iterable):
            for item in obj:
                return TimeObjectAbstract.contains_time_series(item)
        else:
            return isinstance(obj, TimeObjectAbstract)

    @staticmethod
    def apply(func, *args):
        """Apply a function to a 'TimeSeries'.
        
        Parameters:
        - *args: list[any]
            The arguments that should be used as parameters
            in that function.
        """
        return TimeApplyFunc(func, *args)

    def __mul__(self, other):
        return TimeMul(self, other)

    def __truediv__(self, other):
        return TimeDiv(self, other)

    def __rtruediv__(self, other):
        return TimeInvDiv(self, other)
    
    def __add__(self, other):
        return TimeAdd(self, other)

    def __sub__(self, other):
        return TimeSub(self, other)

    def __rsub__(self, other):
        return TimeRevSub(self, other)
    
    def __pow__(self, other):
        return TimePow(self, other)
    
    __rmul__ = __mul__
    __radd__ = __add__

    def __repr__(self):
        raise NotImplementedError()

class TimeOperationAbstract(TimeObjectAbstract):
    """Abstract base class for time-based operations."""
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

class TimeSeries(TimeObjectAbstract):
    """A Python class for adding time-based variables to a numerical expression.

    This class supports all the basic arithmetic operations and is meant to be 
    used alongside numpy arrays to create dynamic time-evaluated coordinates. 
    Applying functions onto a TimeSeries is also possible but most be done through 
    the intermediary static method .apply(...).

    Preview is not available with TimeSerie.

    Attributes:
    - start: int
        Start value.
    - end: int
        End value.
    """
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def evaluate(self, t):
        return self.start + t*(self.end-self.start)

    def __repr__(self):
        return f"TimeSeries({self.start}, {self.end})"

class TimeApplyFunc(TimeObjectAbstract):
    """Apply function operation."""

    def __init__(self, func, *args):
        self.func = func
        self.args = args
    
    def evaluate(self, t):
        return self.func(*[self.evaluate_ext(arg, t) for arg in self.args])
    
    def __repr__(self):
        return f"TimeApplyFunc({self.func}, {', '.join(map(repr, self.args))})"

class TimeMul(TimeOperationAbstract):
    """Multiplication operation."""

    def evaluate(self, t):
        return self.evaluate_ext(self.op1, t) * self.evaluate_ext(self.op2, t)
    
    def __repr__(self):
        return f"TimeMul({repr(self.op1)}, {repr(self.op2)})"

class TimeDiv(TimeOperationAbstract):
    """Division operation."""

    def evaluate(self, t):
        return self.evaluate_ext(self.op1, t) / self.evaluate_ext(self.op2, t)
    
    def __repr__(self):
        return f"TimeDiv({repr(self.op1)}, {repr(self.op2)})"

class TimeInvDiv(TimeOperationAbstract):
    """Inverse division operation."""

    def evaluate(self, t):
        return self.evaluate_ext(self.op2, t) / self.evaluate_ext(self.op1, t)
    
    def __repr__(self):
        return f"TimeInvDiv({repr(self.op1)}, {repr(self.op2)})"

class TimeAdd(TimeOperationAbstract):
    """Addition operation."""

    def evaluate(self, t):
        return self.evaluate_ext(self.op1, t) + self.evaluate_ext(self.op2, t)
    
    def __repr__(self):
        return f"TimeAdd({repr(self.op1)}, {repr(self.op2)})"

class TimeSub(TimeOperationAbstract):
    """Subtraction operation."""

    def evaluate(self, t):
        return self.evaluate_ext(self.op1, t) - self.evaluate_ext(self.op2, t)
    
    def __repr__(self):
        return f"TimeSub({repr(self.op1)}, {repr(self.op2)})"

class TimeRevSub(TimeOperationAbstract):
    """Reverse order subtraction operation."""

    def evaluate(self, t):
        return self.evaluate_ext(self.op2, t) - self.evaluate_ext(self.op1, t)
    
    def __repr__(self):
        return f"TimeRevSub({repr(self.op1)}, {repr(self.op2)})"

class TimePow(TimeOperationAbstract):
    """Power operation."""

    def evaluate(self, t):
        return self.evaluate_ext(self.op1, t)**self.evaluate_ext(self.op2, t)
    
    def __repr__(self):
        return f"TimePow({repr(self.op1)}, {repr(self.op2)})"