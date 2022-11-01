# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import os
import sys
import importlib
import inspect

sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------

project = "meliora"
copyright = "2022, Anton Treialt"
author = "Anton Treialt"

# The full version, including alpha/beta/rc tags
release = "0.2"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.linkcode", "sphinxcontrib.apidoc", "sphinx.ext.napoleon"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# based on the info from
# https://github.com/readthedocs/sphinx-autoapi/issues/202
# https://github.com/aaugustin/websockets/blob/778a1ca6936ac67e7a3fe1bbe585db2eafeaa515/docs/conf.py

from src.meliora import __version__

code_url = f"https://github.com/at621/meliora/blob/{__version__}"


def linkcode_resolve(domain, info):
    # Non-linkable objects from the starter kit in the tutorial.
    if domain != "py":
        return code_url + "?not-python-error"

    mod = importlib.import_module(info["module"])
    if "." in info["fullname"]:
        objname, attrname = info["fullname"].split(".")
        obj = getattr(mod, objname)
        try:
            # object is a method of a class
            obj = getattr(obj, attrname)
        except AttributeError:
            # object is an attribute of a class
            return code_url + "?attribute-get-error"
    else:
        obj = getattr(mod, info["fullname"])

    try:
        file = inspect.getsourcefile(obj)
        lines = inspect.getsourcelines(obj)
    except TypeError:
        # e.g. object is a typing.Union
        return code_url + "?type-error"
    file = os.path.relpath(file, os.path.abspath("../.."))
    if not file.startswith("src/meliora"):
        return code_url + "?filename-error&" + file
    start, end = lines[1], lines[1] + len(lines[0]) - 1

    return f"{code_url}/{file}#L{start}-L{end}"


# The master toctree document.
master_doc = "index"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "css/custom.css",
]

# -- Options for Texinfo output ----------------------------------------


# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "credit_risk_validation_tests",
        "Credit Risk Documentation",
        author,
        "credit_risk_validation_tests",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# apidoc directories
# apidoc_module_dir = '../../meliora'
apidoc_output_dir = "meliora"
apidoc_excluded_paths = ["tests"]
apidoc_separate_modules = True
