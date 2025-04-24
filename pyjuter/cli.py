from pyjuter.module import Module
from sys import argv
from argparse import ArgumentParser


def split_ext (fname):
    split = fname.rsplit (".", maxsplit = 1)
    if len (split) < 2:
        raise Exception (f"Missing filename extension in `{fname}`")
    ext = split [1]
    if ext not in ("ipynb", "py"):
        raise Exception (f"Invalid filename extension: `{ext}`")
    return split

def convert (*, input: str, output: str, inline: list[str]):
    if inline:
        if split_ext (input) == "ipynb":
            raise Exception (
                f"`--inline` is not valid when converting from Python"
            )
    out_fmt = split_ext (output)[1]

    inline_mods = []  # Input, followed by inlined modules and their names
    for inp in (input, *inline):
        name, fmt = split_ext (inp)
        with open (inp) as inp_f:
            source = inp_f.read ()
        match fmt:
            case "ipynb": mod = Module.from_ipynb (source)
            case "py": mod = Module.from_py (source)
            case _: assert False
        inline_mods.append ((mod, name))

    input_mod = inline_mods [0][0]
    for mod, name in inline_mods [1:]:
        input_mod.inline (mod, name)

    match out_fmt:
        case "ipynb": res = input_mod.to_ipynb ()
        case "py": res = input_mod.to_py ()
        case _: assert False
    with open (output, "w") as out_f:
        out_f.write (res)

if __name__ == "__main__":
    ap = ArgumentParser ()
    for arg in ("--input", "--output"):
        ap.add_argument (arg, required = True)
    ap.add_argument ("--inline", nargs = "+", default = [])

    # TODO: Make `--inline` a list of module names instead of file names

    convert (**vars (ap.parse_args ()))
