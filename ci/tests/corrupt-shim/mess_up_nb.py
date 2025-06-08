#!/bin/python3

# Utilities for corrupting Notebooks from Pyjuter
#
# Note that this code is called from Python
# embedded in a shell script; hence the unusual
# program structure.

from nbformat import read, write
from copy import deepcopy

notebook_in = None
notebook_out = None

def load_nb (path):
    global notebook_in, notebook_out
    notebook_in = read (path, as_version = 4)
    notebook_out = deepcopy (notebook_in)

def store_nb (path):
    global notebook_in, notebook_out
    write (notebook_out, path)
    notebook_out = deepcopy (notebook_in)

def mess_up_import_helper ():
    "Corrupt the import shim helper (the first cell)."
    global notebook_in, notebook_out
    # Do something subtle
    notebook_out.cells [0].source += " "

def mess_up_shim (shim_mode):
    "Corrupt the shim of a single cell"
    global notebook_in, notebook_out
    cell = None
    shimspec = None
    for c in notebook_out.cells:
        if cell and shimspec: break
        shims = c.metadata.pyjuter.shims
        if shims:
            for s in shims:
                if s.mode == shim_mode:
                    cell = c
                    shimspec = s

    if shimspec.mode == "pre":
        before = ""
        shim = cell.source [:shimspec.len]
        after = cell.source [shimspec.len:]
    elif shimspec.mode == "post":
        before = cell.source [:-shimspec.len]
        shim = cell.source [-shimspec.len:]
        after = ""
    else:
        assert False

    # Just a little trailing whitespace on the last line
    nl = shim.rfind ("\n")
    shim = shim [:nl] + " " + shim [nl:]
    cell.source = (before + shim + after)
