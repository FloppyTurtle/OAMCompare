import numpy as np

def single(y_error):
    order = np.log10(y_error)
    order = np.floor(float(order))
    print(order)
    error = np.round(y_error,-int(order))
    return error

