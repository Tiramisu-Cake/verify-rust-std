#!/usr/bin/env python3
"""Single local entrypoint for SmallSort assignment/checkpoint/session preparation."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
HELP = """Usage: smallsort-session COMMAND [OPTIONS]

  task create|install ...         Compact next assignment; install only when closed
  checkpoint validate|render|write-views ...
                                 Validate handoff and generate STATUS/task report
  prepare --spec FILE --out DIR   Review-only fresh ledger/profile/recipe bundle
  check --bundle DIR             Recheck prepared bundle against committed inputs
  closure --worktree DIR --commit SHA --recipe PATH
                                 Static Git mode/blob/byte closure inventory
  review create|check ...         Exact committed diff/dependencies for review
  observations record|list|render|check ...
                                 Immutable, bounded Brief navigation records

No Cloud calls, registration, slot reservations, proof tools, commit or push.
New session activation still requires the existing branch client admission.
"""


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print(HELP, end="")
        return 0
    command = args.pop(0)
    if command == "task":
        import assignment
        return assignment.main(args)
    if command == "checkpoint":
        import checkpoint
        return checkpoint.main(args)
    if command in ("prepare", "check", "closure"):
        import session_prepare
        return session_prepare.main([command, *args])
    if command == "review":
        import review_packet
        return review_packet.main(args)
    if command == "observations":
        import observations
        return observations.main(args)
    print("Unknown command: " + command + "\n" + HELP, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
