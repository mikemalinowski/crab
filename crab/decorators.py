

# --------------------------------------------------------------------------------------------------
def deprecated(alternate='undefined'):
    def deprecated_inner(func):
        def wrapper(*args, **kwargs):
            print('CRAB DEPRECATION: {} is deprecated. Please use {} instead.'.format(
                    func.__name__,
                    alternate,
                ),
            )
            return func(*args, **kwargs)
        return wrapper
    return deprecated_inner
