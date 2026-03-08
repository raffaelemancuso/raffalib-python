# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# Problems with imports? Could try `export PYTHONPATH=$PYTHONPATH:`pwd`` from root project dir...
import os
import sys
from pathlib import Path
src_path = Path("../../src")
assert src_path.is_dir()
assert (src_path/"raffalib").is_dir()
sys.path.insert(0, src_path.resolve())  # Source code dir relative to this file

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'raffalib-python'
copyright = '2026, Raffaele Mancuso'
author = 'Raffaele Mancuso'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'autoapi.extension'
]

autoapi_dirs = ['../../src']

exclude_patterns = ['_build', '_templates']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

html_theme = "sphinx_rtd_theme"
