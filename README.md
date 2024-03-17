# pypp

A preprocessor/template engine that uses Python.

Requires Python > 3.7.

## Usage:

  pypp.py [-h] [-u USERMODULE] [-e ENVIRONMENT] [-o OPENTAG] [-c CLOSETAG] [FILE]

  positional arguments:
    FILE                  input file. if no FILE is given, read from stdin.

  options:
    -h, --help            show this help message and exit
    -u USERMODULE, --user-module USERMODULE
                          python module containing user python code, omit .py extension
    -e ENVIRONMENT, --environment ENVIRONMENT
                          extra environment
    -o OPENTAG, --opentag OPENTAG
                          character(s) used as start tag for embedded python code (default: opentag from USERMODULE, '{{' if not defined)
    -c CLOSETAG, --closetag CLOSETAG
                          character(s) used as close tag for embedded python code (default: closetag from USERMODULE, '}}' if not defined)

Reads FILE, evaluates Python code embedded between OPENTAG and CLOSETAG and substitutes it with its result or, if it's
not a string, with its stdout. All embedded code must evaluate to string or produce stdout. Additional Python code can be defined in USERMODULE. WARNING: uses eval(),
don't use on untrustworthy input.
