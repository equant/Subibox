import time

# Unused?
def timing(f):
    """
    Used to benchmark code to discover bottlenecks.  Important since the target
    platform is Pi Zero
    Usage:

    @timing
    def function_you_want_to_time(self, foo bar):
        blah blah blah
    """
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{} function took {:0.3f} ms'.format(f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap

# Unused?
def rgb_to_color_list(rgb_string, alpha=1.):
    """
    "#FFFFFF" -> (1.0, 1.0, 1.0, 1.0)
    "000000"  -> (0.0, 0.0, 0.0, 1.0)
    """
    if rgb_string[0] == '#':
        c = rgb_string[1:]
    else:
        c = rgb_string
    return [int(c[i:i+2],16)/255 for i in range(0, len(c), 2)] + [alpha]
