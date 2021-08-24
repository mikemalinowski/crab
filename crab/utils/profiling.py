import os
import cProfile
from time import time

import pymel.core as pm


def profile_this(func):

    def wrapper(*args, **kwargs):

        # pm.displayInfo('Profiling Started : {}'.format(func.__name__))
        directory = os.path.dirname(os.path.abspath(__file__))
        export_filename = func.__name__ + ".pfl"
        export_path = os.path.join(directory, export_filename)
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(export_path)

        pm.displayInfo('Profile Saved to : {}'.format(export_path))
        return result

    return wrapper


def time_this(func):

    def wrapper(*args, **kwargs):

        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print('func: %r took: %2.4f sec' % (func.__name__, end_time - start_time))

        return result

    return wrapper
