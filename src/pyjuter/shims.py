"""
Various shims for use in notebooks generated by Pyjuter.

Variable names in the shims are prefixed with `_pyjuter_`
to prevent conflicts with names used in the code being handle.
"""

from zlib import adler32
from typing import Dict

module_setup_shim = """
# Not sure why this should be hidden ...
import sys as _pyjuter_sys
# ... nevertheless, consistency

class _pyjuter_ModuleShim:
    @classmethod
    def get (cls, name):
        if name not in _pyjuter_sys.modules:
            _pyjuter_sys.modules [name] = cls ()
        return _pyjuter_sys.modules [name]

    def populate (self, old_global_names, new_globals):
        for name in new_globals:
            if (
                (not name.startswith ("_pyjuter_")) and
                name not in old_global_names
            ):
                self.__setattr__ (name, new_globals [name])
"""

importable_pre = (
    # Goes at the top of the cell
    "_pyjuter_module = _pyjuter_ModuleShim.get ('{module_name}')\n"
    "_pyjuter_old_global_names = set (globals ().keys ())\n\n"
)

importable_post = (
    # Goes at the bottom of the cell
    "\n_pyjuter_new_globals = globals ()\n"
    "_pyjuter_module.populate (_pyjuter_old_global_names, _pyjuter_new_globals)\n"
)

def digest (shim: str, mode: str) -> Dict[str, int|str]:
    """
    Generate the digest for shim `str`.
    `mode` is one of "pre" and "post".

    Returns a dictionary of the form
    `{"len": int, "start": int, "sum": int}`.

    Note: a negative index counts backwards from the end
    of a string; so -2 points to the second-last character.
    """
    b_shim = bytes (shim, encoding = "ascii")
    length = len (shim)
    assert mode == "pre" or mode == "post", (
        "`mode` must be either 'pre' or 'post'"
    )

    return {
        "len": length,
        "mode": mode,
        "sum": adler32 (b_shim),
    }

def strip_shim (source: str, shim_digest: Dict[str, int]) -> str | None:
    """
    Strip a shim from `source`. The expected checksum and position,
    recorded by `shim_digest`, are used to find and validate the shim.
    """
    length, mode = shim_digest ["len"], shim_digest ["mode"]
    match mode:
        case "pre":
            shim = source [0:length]
            code = source [length:]
        case "post":
            code = source [0:-length]
            shim = source [-length:]
        case _: raise Exception ("Invalid mode: `mode`")

    if adler32 (bytes (shim, encoding = "ascii")) != shim_digest ["sum"]:
        return None

    return code
