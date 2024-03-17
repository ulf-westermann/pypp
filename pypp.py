#!/usr/bin/env python3


"""A preprocessor/template engine."""


import argparse
import importlib
import io
import re
import sys
import types


def substitute(input_str: str, tag_open: str, tag_close: str, globals: dict) -> str:
    """Do the actual text substitution."""

    tag_open_esc = re.escape(tag_open)
    tag_close_esc = re.escape(tag_close)
    output_str = input_str

    # regex breakdown:
    #   (?<!\\\)        - lookbehind assertion, matches if the current position in the string is not preceeded by a backslash
    #   {tag_open_esc}  - f-string substitution for escaped open tag
    #   (.*?)           - group that non-greedily matches the actual python code between open and close tag
    #   (?<!\\\)        - lookbehind assertion, matches if the current position in the string is not preceeded by a backslash
    #   {tag_close_esc} - f-string substitution for escaped open tag
    for match in re.finditer(f"(?<!\\\){tag_open_esc}(.*?)(?<!\\\){tag_close_esc}", input_str, re.DOTALL):
        stdout_original = sys.stdout
        sys.stdout = stdout_captured = io.StringIO()

        try:
            code = match.group(1)
            code_result = eval(code, globals)

            if not isinstance(code_result, str):
                code_result = stdout_captured.getvalue()

                if not code_result:
                    raise Exception("code does not evaluate to string and produces no stdout")

            output_str = output_str.replace(match.group(), code_result, 1)
        except Exception as exc:
            sys.stderr.write(f"error at pos {match.start()}: {exc}: {match.group()}\n")
        finally:
            sys.stdout = stdout_original

    return output_str


def run(input_filename: str | None, user_module: types.ModuleType | None, extra_env_dict: dict, opentag: str, closetag: str) -> None:
    """Main function. Figure out configuration, read in file contents, execute substitution and print result."""

    # read input text
    if input_filename is None:
        input_text = sys.stdin.read()
    else:
        with open(input_filename, encoding='utf8') as input_file:
            input_text = input_file.read()

    # run initialize function from macro module
    if user_module is not None and hasattr(user_module, 'initialize'):
        if not user_module.initialize(input_filename):
            raise Exception("initialize failed")

    # augment environment of opts module
    extra_env = vars(user_module) if user_module is not None else {}
    extra_env.update(extra_env_dict)

    # run macro substitution and print result to stdout
    print(substitute(input_text, opentag, closetag, extra_env), end="")

    # run terminate function from macro module
    if user_module is not None and hasattr(user_module, 'terminate'):
        if not user_module.terminate(input_filename):
            raise Exception("terminate failed")


def _get_delimiter_tags(args: dict, user_module: types.ModuleType | None) -> tuple[str, str]:
    """Get delimiter tags. There are 2 possible sources: command argument and opts module. Command line overrides
       opts module. If not defined by these 2 sources, the default is applied (`{{` and `}}`)."""

    if args["opentag"]:
        opentag = args["opentag"]
    elif user_module and hasattr(user_module, "opentag"):
        opentag = user_module.opentag
    else:
        opentag = "{{"

    if args["closetag"]:
        closetag = args["closetag"]
    elif user_module and hasattr(user_module, "closetag"):
        closetag = user_module.closetag
    else:
        closetag = "}}"

    return opentag, closetag


def _parse_arguments() -> dict:
    """Define command line interface and parse actual arguments."""

    parser = argparse.ArgumentParser(description="""Preprocessor/template engine that uses Python.
        Reads FILE, evaluates Python code embedded between OPENTAG and CLOSETAG and substitutes it with its result or,
        if it's not a string, with its stdout. All embedded code must evaluate to string or produce stdout. Additional
        Python code can be defined in USERMODULE. WARNING: uses eval(), don't use on untrustworthy input.""")
    parser.add_argument("-u", "--user-module", metavar="USERMODULE", help="python module containing user python code, omit .py extension")
    parser.add_argument("-e", "--environment", default="{}", help="extra environment")
    parser.add_argument("-o", "--opentag", help="character(s) used as start tag for embedded python code (default: opentag from USERMODULE, '{{' if not defined)")
    parser.add_argument("-c", "--closetag", help="character(s) used as close tag for embedded python code (default: closetag from USERMODULE, '}}' if not defined)")
    parser.add_argument("file", nargs="?", metavar="FILE", help="input file. if no FILE is given, read from stdin.")

    return vars(parser.parse_args())


if __name__ == "__main__":
    args = _parse_arguments()

    user_module = importlib.import_module(args["user_module"]) if args["user_module"] is not None else None
    input_filename = args['file']
    extra_env_dict = eval(args['environment'])
    opentag, closetag = _get_delimiter_tags(args, user_module)

    run(input_filename, user_module, extra_env_dict, opentag, closetag)

