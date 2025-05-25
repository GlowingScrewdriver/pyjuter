from pyjuter.cli import (
    process_args,
    dispatch_command,
    CLIError,
)
from sys import argv

if __name__ == "__main__":
    # TODO: Help message
    try:
        cmd, opts = process_args (argv [1:])
        dispatch_command (cmd, opts)
    except CLIError as e:
        print (f"Bad usage: {e}")
        print ("Run `pyjuter -h` for help")
