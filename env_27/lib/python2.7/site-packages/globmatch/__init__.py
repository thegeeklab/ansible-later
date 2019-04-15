#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Simula Research Laboratory.
# Distributed under the terms of the Modified BSD License.

"""Utilities for matching a path against globs."""

import os

from .translation import compile_pattern
from ._version import __version__


def glob_match(path, globs):
    """Matches a path against a sequence of globs."""
    path = os.path.normcase(path)
    for g in globs:
        matcher = compile_pattern(g)
        if matcher(path):
            return True
    return False

__all__ = ['glob_match', '__version__']
