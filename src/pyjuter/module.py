#!/bin/env python3

"""
Script to convert a Python source tree to a Jupyter Notebook
and vice-versa.
"""

from nbformat import (
    reads,    # TODO: Import with an alias?
    writes,
    validate,
)
from nbformat.v4 import (
    new_notebook,
    new_code_cell,
)
from collections.abc import Iterable
from typing import Self

import pyjuter.shims as shims


class Chunk:
    """
    A single code chunk. This can be a part of a file from a Python
    source tree or a cell in a Jupyter Notebook.
    """
    file: str | None
    """
    The Python source file from which this chunk originated;
    `None` in the case of the main module.
    """

    def __init__ (self, source: str, modname: str = None, *, importable = False) -> Self:
        self.source = source
        if importable:
            assert modname is not None
        self.modname = modname
        self.importable = importable

    def as_nb_cell (self) -> dict:
        "Render as a Jupyter Notebook cell"
        cell = new_pyjuter_code_cell ()

        if self.importable:
            pre = shims.importable_pre.format (module_name = self.modname)
            post = shims.importable_post
            src = "".join ((
                pre,
                self.source,
                post,
            ))
            cell.metadata.pyjuter.shims = {
                "pre": shims.digest (pre),
                "post": shims.digest (post),
            }
        else:
            src = self.source

        cell.source = src
        return cell

    def as_py (self) -> str:
        "Render as a chunk of Python source"
        return self.source

class Module:
    """
    Abstraction of Python source trees and Jupyter Notebooks.
    """

    cells: list[Chunk]

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
        res.chunks = [
            Chunk (c)
            for c in split_toplevel_stmts (source)
        ]
        return res

    @classmethod
    def from_ipynb (cls, source: str) -> Self:
        """
        Construct from a Jupyter Notebook read from `source`.
        """
        nb = reads (source, as_version = 4)
        res = cls ()
        res.metadata = nb ["metadata"]
        res.chunks = [
            # TODO: Verify cell type
            Chunk (cell.source)
            for cell in nb.cells
        ]
        return res

    def to_py (self) -> str:
        """
        Render as Python source.
        """
        return "\n".join ((
            c.as_py ()
            for c in self.chunks
        ))

    def to_ipynb (self) -> str:
        """
        Render as Jupyter Notebook.
        """
        nb = new_notebook ()
        cells = (
            c.as_nb_cell ()
            for c in self.chunks
        )
        nb.cells = [
            new_code_cell (source = shims.module_setup_shim),
            *cells,
        ]

        validate (nb)
        return writes (nb)

    def inline (self, other: str, modname: str):
        """
        Inline `other` into `self`. This entails including all
        of `other`'s chunks in `self` and setting up the import
        shim to allow access to `other`'s contents.
        """
        other_chunks = (
            Chunk (c, modname = modname, importable = True)
            for c in split_toplevel_stmts (other)
        )
        self.chunks = [
            *other_chunks,
            *self.chunks,
        ]

def split_toplevel_stmts (source: str) -> Iterable[str]:
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
    for line in source.split ("\n"):
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

def new_pyjuter_code_cell ():
    """Wrapper around `new_code_cell`"""
    cell = new_code_cell ()
    cell.metadata.pyjuter = {
        "shims": None,
    }
    return cell
