from sys import argv
from argparse import ArgumentParser

from pyjuter.module import Module


# Handler functions implementing each command
def convert_py_to_ipynb (inp: str, inline: list[tuple[str, str]], out: str):
    """
    Convert Python sources to a Jupyter Notebook.
    The source program is loaded from file `inp`. `inline` is
    a list of (module name, source file) to be inlined. The
    result is written to `out`.
    """
    with open (inp) as f:
        src = f.read ()
    module = Module.from_py (src, inp)

    for modname, fname in inline:
        with open (fname) as f:
            src = f.read ()
        module.inline (src, modname, fname)

    with open (out, "w") as f:
        f.write (module.to_ipynb ())

def convert_ipynb_to_py (inp: str):
    """
    Convert a Jupyter Notebook to the original Python
    source files.
    """
    with open (inp) as f:
        src = f.read ()
    module = Module.from_ipynb (src)

    print (module.to_py ())

# Command line parsing utilities
OPTION_COUNTS = {
    # Number of allowed values for an option
    # `None` indicates no restriction
    "-inline": None,
    "-input": 1,
    "-output": 1,
}
COMMAND_OPTIONS = {
    # Options allowed for each command
    "p2j": {"-inline", "-input", "-output"},
    "j2p": {"-input"},
}

def process_args (args: list[str]):
    """
    Process and verify command-line arguments
    """
    if not args:
        raise Exception ("Expected a command")
    command = args.pop (0)
    if command not in COMMAND_OPTIONS:
        raise Exception (f"Invalid command: {command}")
    options = {
        opt: []
        for opt in COMMAND_OPTIONS [command]
    }

    while args:
        # Get the next option
        opt = args.pop (0)
        if not opt.startswith ("-"):
            raise Exception ("{opt}: Expected an option")
        if opt not in options:
            raise Exception (
                f"Invalid option {opt} for command {command}"
            )

        # Get the values for this option
        while args and (not args [0].startswith ("-")):
            options [opt].append (args.pop (0))

    for opt in options:
        ecount = OPTION_COUNTS [opt]
        if ecount is not None:
            if len (options [opt]) != ecount:
                raise Exception (f"Expected {ecount} values for {opt}")

    return command, options

def dispatch_command (cmd: str, opts: dict[str, str]):
    """
    Map command line to handler functions.
    Although this can be automated, manually enumerating everything here
    will help catch discrepancies between the CLI and Python interfaces.
    """
    match cmd:
        case "p2j":
            inline = []
            for val in opts ["-inline"]:
                modname, fname = val.split ("=")
                if not (modname and fname):
                    raise Exception (
                        f"Values passed to `-inline` must be of the form\n"
                        "<module name>=<source file>"
                    )
                inline.append ((modname, fname))
            convert_py_to_ipynb (
                opts ["-input"][0],
                inline,
                opts ["-output"][0],
            )
        case "j2p":
            convert_ipynb_to_py (opts ["-input"][0])
        case _:
            assert False


if __name__ == "__main__":
    # TODO: Help message
    cmd, opts = process_args (argv [1:])
    dispatch_command (cmd, opts)
