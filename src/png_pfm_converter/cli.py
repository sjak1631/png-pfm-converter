import argparse
import sys

from .converter import pfm_to_png, png_to_pfm


def png2pfm() -> None:
    parser = argparse.ArgumentParser(
        prog="png2pfm",
        description="Convert PNG to PFM (Portable Float Map).",
    )
    parser.add_argument("input", help="Input PNG file")
    parser.add_argument("output", help="Output PFM file")
    args = parser.parse_args()

    try:
        png_to_pfm(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def pfm2png() -> None:
    parser = argparse.ArgumentParser(
        prog="pfm2png",
        description="Convert PFM (Portable Float Map) to PNG.",
    )
    parser.add_argument("input", help="Input PFM file")
    parser.add_argument("output", help="Output PNG file")
    args = parser.parse_args()

    try:
        pfm_to_png(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
