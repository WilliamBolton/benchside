"""The `bench` entry point.

Two faces, one binary:

  runtime (called from skill bash blocks)
    bench log <event>        append a journal event
    bench recall <line>      what the persona reads at the start of a sitting
    bench consent ...        grant, revoke, show
    bench export --preview   render the exact bytes an export would send

  dev (called by contributors and CI)
    bench compile            personas + templates -> skills/ and judge rubrics
    bench check              freshness and validation dashboard

Subcommands parse arguments into a Command or Query DTO, resolve the matching
handler from the container inside a UOW scope, and print the Result.
"""

import sys


def main(argv: list[str] | None = None) -> int:
    raise NotImplementedError("bench CLI not implemented yet")


if __name__ == "__main__":
    sys.exit(main())
