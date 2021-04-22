from pathlib import Path
from typing import Optional
import argparse
import os
import sys


# copied from https://stackoverflow.com/a/10551190
class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


# singleton argument parser
_argument_parser: Optional[argparse.ArgumentParser] = None


def argument_parser_factory(
    *, reference=None, logfile: Path = None
) -> argparse.ArgumentParser:
    global _argument_parser
    if _argument_parser:
        return _argument_parser

    _argument_parser = argparse.ArgumentParser(usage="%(prog)s [-h] [options]")
    p = _argument_parser

    p.add_argument(
        "--reference",
        default=reference or Path(sys.argv[0]).stem,
        help=(
            "Identifer to reference all the emails sent by this script (sent to Notify)."
            " Defaults to the name of the script."
        )
    )

    # As this log will contain PII, we want to make sure it doesn't sit on
    # a developers drive for too long, however, we do need to be able to
    # find the logs again for resuming a run or for audit purposes.
    #
    # So for a default we just go ahead and assume that there is a /tmp folder,
    # which is true everywhere except Windows.
    p.add_argument(
        "--logfile",
        type=Path,
        default=logfile or Path("/tmp", f"{p.get_default('reference')}.log"),
        help=(
            "File where log messages will be saved so that the script can resume if interrupted."
            " By default logs are saved in the system tmp folder with the name of the script."
        )
    )

    p.add_argument(
        "--notify-api-key",
        action=EnvDefault,
        envvar="DM_NOTIFY_API_KEY",
        help="Can also be set with environment variable DM_NOTIFY_API_KEY.",
        required=True,
    )
    p.add_argument(
        "--dry-run", "-n", action="store_true", help="Do not send notifications."
    )

    p.add_argument(
        "--stage",
        action=EnvDefault,
        envvar="DM_ENVIRONMENT",
        help="Stage/environment to make API calls to. Can also be set with environment variable DM_ENVIRONMENT.",
        required=True,
    )

    p.add_argument(
        "--notify-template-id",
        help="The Notify template ID for this email",
        required=False
    )

    return p


if __name__ == "__main__":
    argument_parser_factory().parse_args(["--help"])
