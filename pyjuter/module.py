#!/bin/env python3

"""
Script to convert a Python source tree to a Jupyter Notebook
and vice-versa.
"""

from nbformat import (
    reads,
    writes,
    validate,
)
from nbformat.v4 import (
    new_notebook,
    new_code_cell,
)
from collections.abc import Iterable
from typing import Self

from pyjuter.shims import module_setup_shim, chunk_as_module


class Module:
    @classmethod
    def from_py (cls, source: str) -> Self:
        """
        Construct from Python source code read from `source`.
        """
        res = cls ()
        res.metadata = {
            "language_info": {
                "name": "python",
            }
        }
        lines = source.split ("\n")
        res.chunks = [*split_toplevel_stmts (lines)]
        return res

    @classmethod
    def from_ipynb (cls, source: str) -> Self:
        """
        Construct from a Jupyter Notebook read from `source`.
        """
        res = cls ()
        res.chunks = []
        res.metadata = nb ["metadata"]
        nb = reads (source, as_version = 4)
        for cell in nb.cells:
            # TODO: Verify cell type
            res.chunks.append (cell.source)
        return res

    def to_py (self) -> str:
        """
        Render as Python source.
        """
        return "\n".join (self.chunks)

    def to_ipynb (self) -> str:
        """
        Render as Jupyter Notebook.
        """
        nb = new_notebook ()
        for chunk in (module_setup_shim, *self.chunks):
            cell = new_code_cell (source = chunk)
            nb.cells.append (cell)

        validate (nb)
        return writes (nb)

    def inline (self, other: Self, modname: str):
        """
        Inline `other` into `self`. This entails including all
        of `other`'s chunks in `self` and setting up the import
        shim to allow access to `other`'s contents.
        """
        # TODO: Operate on cells instead of chunks, so we can do
        # some metadata magic
        self.chunks = [
            *(chunk_as_module (modname, chunk) for chunk in other.chunks),
            *self.chunks,
        ]

def split_toplevel_stmts (source: Iterable[str]) -> Iterable[str]:
    """
    Split the provided Python source into chunks on the basis of
    blank lines between top-level statements.

    The intention is for each chunk to become a cell in a
    Jupyter Notebook.

    `source` is an iterator over lines of the source
    (excluding newline characters).
    An iterator over the resulting chunks (without trailing
    newlines) is returned.
    """
    chunk = []
    lastline = None
    for line in source:
        if line:
            if not line [0].isspace ():
                # This is the beginning of a statement ... ->
                if lastline == "":
                   # -> ... after a blank line
                   yield "\n".join (chunk)
                   chunk = []

        chunk.append (line)
        lastline = line

    # Don't forget the last chunk!
    if chunk:
        yield "\n".join (chunk)
