#!/usr/bin/env python3
"""
A small utility that divides two numbers.

The function `divide` performs a division and raises a ValueError
if the divisor is zero.  The module can also be executed from the
command line to perform a division of two numbers supplied as
arguments.
"""

from __future__ import annotations

import argparse
import sys


def divide(a: float, b: float) -> float:
    """
    Return the result of dividing *a* by *b*.

    Parameters
    ----------
    a : float
        The dividend.
    b : float
        The divisor.

    Returns
    -------
    float
        The quotient of *a* divided by *b*.

    Raises
    ------
    ValueError
        If *b* is zero.
    """
    if b == 0:
        raise ValueError("The divisor 'b' must not be zero.")
    return a / b


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Divide two numbers and print the result."
    )
    parser.add_argument(
        "dividend",
        type=float,
        help="The number to be divided.",
    )
    parser.add_argument(
        "divisor",
        type=float,
        help="The number by which to divide.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    try:
        result = divide(args.dividend, args.divisor)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    else:
        print(result)


if __name__ == "__main__":
    main()