#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import numpy as np
from tslearn.cycc import normalized_cc
from itertools import product
# from tslearn.preprocessing import TimeSeriesScalerMeanVariance, TimeSeriesScalerMinMax
# from sklearn.metrics import pairwise_distances


def ncc_c(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Must pass 1D vectors to both x and y

    :param x: Input vector [x1, x2, x3, ... xn]
    :param y: Input vector [y2, y2, x3, ... yn]
    :return:  Returns the normalized cross correlation function (as a vector) of the two input vector arguments "x" and "y"
    """
    cc = normalized_cc(x.reshape(-1, 1), y.reshape(-1, 1))
    return cc


def get_omega(x: np.ndarray = None, y: np.ndarray = None, cc: np.ndarray = None) -> int:
    """
    Must pass a 1D vector to either both "x" and "y" or a cross-correlation function to "cc"

    :param x: Input vector [x1, x2, x3, ... xn]
    :param y: Input vector [y2, y2, x3, ... yn]
    :param cc: cross-correlation function represented as a vector [c1, c2, c3, ... cn]
    :return: index (x-axis position) of the global maxima of the cross-correlation function
    """
    if cc is None:
        cc = ncc_c(x, y)
    w = np.argmax(cc)
    return w


def get_lag(x: np.ndarray = None, y: np.ndarray = None, cc: np.ndarray = None) -> float:
    """
    Must pass a 1D vector to either both "x" and "y" or a cross-correlation function to "cc"

    :param x: Input vector [x1, x2, x3, ... xn]
    :param y: Input vector [y2, y2, x3, ... yn]
    :param cc: cross-correlation function represented as a vector [c1, c2, c3, ... cn]
    :return: Position of the maxima of the cross-correlation function with respect to middle point of the cross-correlation function
    """
    if cc is None:
        w = get_omega(x, y)
        s = w - x.shape[0]
    else:
        w = get_omega(cc=cc)
        s = w - int(cc.shape[0] / 2)
    return float(-s)


def get_epsilon(x: np.ndarray = None, y: np.ndarray = None, cc: np.ndarray = None) -> float:
    """
    Must pass a 1D vector to either both "x" and "y" or a cross-correlation function to "cc"

    :param x: Input vector [x1, x2, x3, ... xn]
    :param y: Input vector [y2, y2, x3, ... yn]
    :param cc: cross-correlation function represented as a vector [c1, c2, c3, ... cn]
    :return: Magnitude of the global maxima of the cross-correlationn function
    """
    if cc is None:
        cc = ncc_c(x, y)
    e = np.max(cc)
    return e


# if normalize == 'z':
#     data = TimeSeriesScalerMeanVariance().fit_transform(data)[:, :, 0]
# elif normalize == 'minmax':
#     data = TimeSeriesScalerMinMax().fit_transform(data)[:, :, 0]

def get_lag_matrix(curves: np.ndarray = None, ccs: np.ndarray = None) -> np.ndarray:
    if ccs is None:
        m = curves.shape[0]
        a = np.zeros((m, m))
        for i in range(m):
            for j in range(m):
                a[i, j] = get_lag(curves[i], curves[j])
        return a

    return _compute_from_ccs(ccs, get_lag)


def get_epsilon_matrix(curves: np.ndarray = None, ccs: np.ndarray = None) -> np.ndarray:
    if ccs is None:
        m = curves.shape[0]
        a = np.zeros((m, m))
        for i in range(m):
            for j in range(m):
                a[i, j] = get_epsilon(curves[i], curves[j])
        return a

    return _compute_from_ccs(ccs, get_epsilon)


def _compute_from_ccs(ccs: np.ndarray, func: callable) -> np.ndarray:
    m = ccs.shape[0]
    a = np.zeros(shape=(m, m))
    for i in range(m):
        for j in range(m):
            a[i, j] = func(cc=ccs[i, j, :])
    return a
