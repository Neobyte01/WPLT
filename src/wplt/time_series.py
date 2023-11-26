import numpy as np
from collections.abc import Iterable

class TimeObjectAbstract:
    TIME_RANGE = 100

    def evaluate(self, t):
        raise NotImplementedError()
    
    @staticmethod
    def evaluate_ext(ext, t):
        if isinstance(ext, TimeObjectAbstract):
            return ext.evaluate(t)
        elif isinstance(ext, Iterable):
            return np.asarray([TimeSeries.evaluate_ext(item, t) for item in ext], dtype=float)
        else:
            return ext
        
    @staticmethod
    def evaluate_total(obj, t):
        if isinstance(obj, Iterable):
            return np.array([TimeSeries.evaluate_ext(item, t) for item in obj])
        else:
            return TimeSeries.evaluate_ext(obj, t)

    @staticmethod
    def contains_time_series(obj):
        if isinstance(obj, Iterable):
            for item in obj:
                return TimeObjectAbstract.contains_time_series(item)
        else:
            return isinstance(obj, TimeObjectAbstract)

    @staticmethod
    def apply(func, *args):
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
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

class TimeSeries(TimeObjectAbstract):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def evaluate(self, t):
        return self.start + t*(self.end-self.start)

    def __repr__(self):
        return f"TimeSeries({self.start}, {self.end})"

class TimeApplyFunc(TimeObjectAbstract):
    def __init__(self, func, *args):
        self.func = func
        self.args = args
    
    def evaluate(self, t):
        return self.func(*[self.evaluate_ext(arg, t) for arg in self.args])
    
    def __repr__(self):
        return f"TimeApplyFunc({self.func}, {', '.join(map(repr, self.args))})"

class TimeMul(TimeOperationAbstract):
    def evaluate(self, t):
        return self.evaluate_ext(self.op1, t) * self.evaluate_ext(self.op2, t)
    
    def __repr__(self):
        return f"TimeMul({repr(self.op1)}, {repr(self.op2)})"

class TimeDiv(TimeOperationAbstract):
    def evaluate(self, t):
        return self.evaluate_ext(self.op1, t) / self.evaluate_ext(self.op2, t)
    
    def __repr__(self):
        return f"TimeDiv({repr(self.op1)}, {repr(self.op2)})"

class TimeInvDiv(TimeOperationAbstract):
    def evaluate(self, t):
        return self.evaluate_ext(self.op2, t) / self.evaluate_ext(self.op1, t)
    
    def __repr__(self):
        return f"TimeInvDiv({repr(self.op1)}, {repr(self.op2)})"

class TimeAdd(TimeOperationAbstract):
    def evaluate(self, t):
        return self.evaluate_ext(self.op1, t) + self.evaluate_ext(self.op2, t)
    
    def __repr__(self):
        return f"TimeAdd({repr(self.op1)}, {repr(self.op2)})"

class TimeSub(TimeOperationAbstract):
    def evaluate(self, t):
        return self.evaluate_ext(self.op1, t) - self.evaluate_ext(self.op2, t)
    
    def __repr__(self):
        return f"TimeSub({repr(self.op1)}, {repr(self.op2)})"

class TimeRevSub(TimeOperationAbstract):
    def evaluate(self, t):
        return self.evaluate_ext(self.op2, t) - self.evaluate_ext(self.op1, t)
    
    def __repr__(self):
        return f"TimeRevSub({repr(self.op1)}, {repr(self.op2)})"

class TimePow(TimeOperationAbstract):
    def evaluate(self, t):
        return self.evaluate_ext(self.op1, t)**self.evaluate_ext(self.op2, t)
    
    def __repr__(self):
        return f"TimePow({repr(self.op1)}, {repr(self.op2)})"