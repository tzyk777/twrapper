"""
example decorator w/ argument

def _require_connection(logger):
    def real_decorator(func):
        def wrapper(self, *args, **kwargs):
            if not self.connected:
                logger.warn('Client is not connected.')
                return
            func(self, *args, **kwargs)
        return wrapper
    return real_decorator
"""


def _require_connection(func):
    def wrapper(self, *args, **kwargs):
        if not self.connected:
            self.logger.warn('{} is not connected.'.format(self))
            return
        return func(self, *args, **kwargs)
    return wrapper
