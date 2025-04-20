#!/bin/env python3

"""
Script to convert a Python source tree to a Jupyter Notebook
and vice-versa.
"""

from ast import (
    parse,
    get_source_segment,
    AST
)
from nbformat import (
    reads,
    writes,
    validate,
)
from nbformat.v4 import (
    new_notebook,
    new_code_cell,
)

class NotAstNode (AST):
    """
    Anything at the top level that is not parsed by `ast.parse`,
    but which is required to preserve style.
    """
    def __init__ (self, start_line, start_col, end_line, end_col):
        self.lineno = start_line
        self.col_offset = start_col
        self.end_lineno = end_line
        self.end_col_offset = end_col
        self._fields = []

class Module:
    @classmethod
    def from_py (cls, source: str):
        """
        Construct from Python source code read from `source`.
        """
        res = cls ()
        res.src = source
        res.ast = parse (res.src)

        # For every pair of consecutive top-levels that has a gap
        # between the end of the first and start of the second, we
        # capture whatever is in the gap using an `NotAstNode`.
        new_body = []
        prev_lineno = 0  # The last line that was accounted for
        for decl in res.ast.body:
            assert decl.col_offset == 0, (
                "We're assuming top-level statements start at col 0 right??"
            )
            if decl.lineno != prev_lineno + 1:
                nan = NotAstNode (prev_lineno + 1, 0, decl.lineno - 1, 0)
                new_body.append (nan)
            new_body.append (decl)
            # TODO: Handle trailing spaces
            prev_lineno = decl.end_lineno

        res.ast.body = new_body
        return res

    @classmethod
    def from_ipynb (cls, source: str):
        """
        Construct from a Jupyter Notebook read from `source`.
        """
        nb = reads (source, as_version = 4)
        cell_srcs = []
        for cell in nb.cells:
            # TODO: Verify cell type
            cell_srcs.append (cell.source)
        src = "\n".join (cell_srcs)
        return cls.from_py (src)

    def to_py (self) -> str:
        """
        Render as Python source.
        """
        res = ""
        for decl in self.ast.body:
            try:
                res += get_source_segment (self.src, decl) + "\n"
            except:
                print (decl)

        return res

    def to_ipynb (self) -> str:
        """
        Render as Jupyter Notebook.
        """
        nb = new_notebook ()
        for decl in self.ast.body:
            src = get_source_segment (self.src, decl)
            cell = new_code_cell (source = src)
            nb.cells.append (cell)

        validate (nb)        
        return writes (nb)
