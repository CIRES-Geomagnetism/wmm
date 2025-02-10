from typing import Optional, Tuple, Union
import numpy as np
def to_npFloatarr(num: Union[float, list, tuple]) -> np.ndarray:
    '''

    :param num: num: The float, list or tuple type of inputs
    :return: numpy array
    '''

    if (np.isscalar(num)):
        return np.array([num])

    elif isinstance(num, (list, tuple, np.ndarray)):
        return np.array(num)

    else:
        raise TypeError("Input must be a float, list, or tuple.")

def to_npIntarr(num: Union[float, list, tuple]) -> np.ndarray:
    '''

    :param num: num: The float, list or tuple type of inputs
    :return: numpy array
    '''

    if (np.isscalar(num)):
        return np.array([num])
    if isinstance(num, (list, tuple, np.ndarray)):
        arr = np.array(num, dtype=int)
    else:
        raise TypeError("Input must be a int or a list/tuple included int.")

    return arr



