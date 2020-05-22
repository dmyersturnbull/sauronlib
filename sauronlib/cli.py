"""
Command-line interface for sauronlib.
"""

from __future__ import annotations

import logging

import typer

logger = logging.getLogger(__package__)

from sauronlib import __title__, __version__, __copyright__, metadata


class Options:
    def __init__(self, verbose: bool):
        self.verbose = verbose

global_options = None

def context(verbose: bool = False):
    """
    Run ${display}, which is a Python project that does something.

    Args:

        verbose: Print extended information.
    """
    global_options = Options(verbose=verbose)


cli = typer.Typer(context=context)


def info(n_seconds: float = 0.01) -> None:
    """
    Get info about sauronlib.

    Args:

        n_seconds: Number of seconds to wait between processing.
    """
    typer.echo("{} version {}, {}".format(__title__, __version__, __copyright__))
    if global_options.verbose:
        typer.echo(str(metadata.__dict__))
    total = 0
    with typer.progressbar(range(100)) as progress:
        for value in progress:
            time.sleep(n_seconds)
            total += 1
    typer.echo(f"Processed {total} things.")


if __name__ == "__main__":
    cli()
