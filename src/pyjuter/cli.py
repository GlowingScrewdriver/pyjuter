from pyjuter.module import Module


class CLIError (Exception):
    pass


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

    for fname, src in module.to_py ().items ():
        with open (fname, "w") as f:
            f.write (src)


# Command line parsing utilities
class OptionValues (list):
    def __init__ (
        self, count: int, optional: bool,
        syntax: str, description: str
    ):
        super ().__init__ (self)
        assert count >= -1
        # TODO: use some word other than "optional"?
        self.optional, self.count, self.description, self.syntax = (
            optional, count, description, syntax)
        self.finished = False

    def read_values (self, args: list [str]):
        if self.finished:
            raise CLIError ("Option specified more than once")
        self.finished = True

        while args and not args [0].startswith ("-"):
            self.append (args.pop (0))
        nvals = len (self)
        if self.count == -1:
            if nvals < 1:
                raise CLIError (f"Expected at least 1 value")
        else:
            if nvals != self.count:
                raise CLIError (f"Expected {self.count} values")

class CommandOptions (dict):
    def __init__ (self, options: dict[str, OptionValues]):
        super ().__init__ (options)

    def read_options (self, args: list [str]):
        while args:
            optname = args.pop (0)
            if not optname.startswith ("-"):
                raise CLIError (f"Expected an option: {optname}")
            option = self.get (optname)
            if option is None:
                raise CLIError (f"Invalid option: {optname}")
            try:
                option.read_values (args)
            except CLIError as e:
                raise CLIError (f"{optname}: {e}")

        # Verify presence of compulsory options
        for optname, option in self.items ():
            if option.optional:
                continue
            if not option.finished:
                raise CLIError (f"Missing option: {optname}")

    def options_summary (self):
        return "\n".join ((
            "   {:<40}   {}".format (
                optname + " " + option.syntax, option.description)
            for optname, option in self.items ()
        ))

COMMANDS = {
    "p2j": CommandOptions ({
        "-input": OptionValues (
            count = 1, optional = False,
            syntax = "<filename>",
            description = "input Python source file"
        ),
        "-inline": OptionValues (
            count = -1, optional = True,
            syntax = "<modname>=<filename> ...",
            description = "inline each <filename> as module <modname>"
        ),
        "-output": OptionValues (
            count = 1, optional = False,
            syntax = "<filename>",
            description = "output Jupyter Notebook"
        ),
    }),
    "j2p": CommandOptions ({
        "-input": OptionValues (
            count = 1, optional = False,
            syntax = "<filename>",
            description = "input Jupyter Notebook"
        ),
    }),
}

def print_help (cmdname = None):
    print ("Usage: -h | pyjuter <subcommand> [-<option1> [<value1> [<value2> ... ]]] ...")
    if cmdname is None:
        print (
            "Run `pyjuter <cmd> -h` for help on subcommand <cmd>\n",
            "Available subcommands:",
            *(
                "  " + cmdname
                for cmdname in COMMANDS
            ),
            sep = "\n"
        )
    else:
        print (
            f"Available options for subcommand `{cmdname}`",
            COMMANDS [cmdname].options_summary (),
            sep = "\n"
        )

def process_args (args: list [str]):
    if not args:
        raise CLIError (f"Expected a command")

    cmdname = args.pop (0)
    if cmdname.startswith ("-"):
        if cmdname == "-h":
            # Make an exception for `pyjuter -h`
            return "_help", {"cmd": None}
        raise CLIError (f"Expected a command: {cmdname}")

    command = COMMANDS.get (cmdname)
    if command is None:
        raise CLIError (f"Invalid command: {cmdname}")

    # Make an exception for `pyjuter <subcommand> -h`
    if "-h" in args:
        return "_help", {"cmd": cmdname}
    command.read_options (args)
    return cmdname, command

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
                modname_fname = val.split ("=")
                if len (modname_fname) != 2:
                    raise CLIError (
                        f"Values passed to `-inline` must be of the form\n"
                        "<module name>=<source file>"
                    )
                inline.append (modname_fname)
            convert_py_to_ipynb (
                opts ["-input"][0],
                inline,
                opts ["-output"][0],
            )
        case "j2p":
            convert_ipynb_to_py (opts ["-input"][0])

        # The following can only be generated internally
        case "_help":
            print_help (opts ["cmd"])
        case _:
            assert False
