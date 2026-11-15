"""Command-line entry point: `python -m harmonize {info,check}`."""

import argparse
import sys

from harmonize.python import diagnostics


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m harmonize",
        description="Inspect Harmonize's GPU platform setup.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "info", help="Report the detected GPU platform, toolchain, and devices."
    )
    commands.add_parser(
        "check",
        help="Report problems that would stop Harmonize from building GPU programs; "
        "exits non-zero if any are found.",
    )
    args = parser.parse_args(argv)

    info = diagnostics.collect_info()
    if args.command == "info":
        print(diagnostics.format_info(info))
        return 0

    findings = diagnostics.run_checks(info)
    print(diagnostics.format_findings(findings))
    if any(finding.level == "error" for finding in findings):
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
