#!/usr/bin/env python
# DFX Finance, 2023


def abs_diff(a, b):
    return abs(a - b)


def rel_diff(a, b):
    return abs(a - b) / max(abs(a), abs(b))


# Compares 2 numbers by a delta value. When `rel=True`, the a and b values will be compared
# by their relative distance. By default, the a and b values are compared by an absolute value.
def approximately_equals(a, b, delta, rel=False):
    if rel:
        return rel_diff(a, b) <= delta
    return abs_diff(a, b) <= delta
