# Author: Álvaro Parafita (parafita.alvaro@gmail.com)

import time

from functools import wraps


def retry(*exceptions, times=1):
    """
        Decorator that executes a function catching the specified exceptions.
        If such an Exception is raised, 
        it retries the whole function at most 'times' times.

        If some other exception than those specified is raised, 
        it won't be catched.

        If retry < 0, infinite loop while an exception inside "exceptions"
        is raised.

        If no exceptions are passed, Exception is the default.
    """

    exceptions = exceptions or (Exception,)


    def dec(func):
        from functools import wraps
        
        @wraps(func)
        def f(*args, **kwargs):
            infinite = times < 0
            iters = 1 if infinite else times + 1

            while True:
                exc = None
                for _ in range(iters):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        print("Exception raised: {}".format(repr(e)))
                        exc = e

                # Exception occured and we made too many retries
                if not infinite:
                    raise exc

                # else, try again
        
        return f

    return dec


def quota(arg=100):
    """
        Decorator that delays the execution of a function
        until a specified lapse time has passed.
        Its argument can be the maximum number of executions run per second
        (then being the time lapse 1 / x) or the function to decorate,
        supposing that the time lapse should be 1 / 100.

        Example:
            # wait 1 / 100 seconds per execution
            @quota
            def f():
                pass

            # wait 1 / 50 seconds per execution
            @quota(50)
            def f():
                pass
    """

    lapse = 1 / (arg if type(arg) == int else 100)

    def dec(func):

        @wraps(func)
        def f(*args, **kwargs):
            (time.wait if hasattr(time, 'wait') else time.sleep)(lapse)
            return func(*args, **kwargs)

        return f


    if type(arg) == int:
        return dec
    else:
        return dec(arg) # arg is then the function to decorate, so decorate it