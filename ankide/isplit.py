# -*- coding: utf-8 -*-
# https://gist.github.com/davidshepherd7/2857bfc620a648a90e7f

import re


def isplit(string, delimiter=None):
    """Like string.split but returns an iterator (lazy)

    Multiple character delimters are not handled.
    """
    if delimiter is None:
        # Handle whitespace by default
        delim = r"\s"

    elif len(delimiter) != 1:
        raise ValueError("Can only handle single character delimiters", delimiter)

    else:
        # Escape, incase it's "\", "*" etc.
        delim = re.escape(delimiter)

    return (x.group(0) for x in re.finditer(r"[^{}]+".format(delim), string))
