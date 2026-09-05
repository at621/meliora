"""Sphinx configuration for the installed public Meliora package."""

from meliora import __version__

project = 'Meliora'
author = 'Anton Treialt and contributors'
copyright = '2026, Meliora contributors'
release = __version__
extensions = ['sphinx.ext.doctest', 'myst_parser']
html_theme = 'alabaster'
exclude_patterns = []
