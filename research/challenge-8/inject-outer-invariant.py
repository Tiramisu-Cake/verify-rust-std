#!/usr/bin/env python3
"""Inject the proof-only outer-loop invariant into a disposable source copy."""

import argparse
from pathlib import Path


ANCHOR = """        let mut tail = v_base.add(offset);
        while tail != v_end {"""

INVARIANTS = """        let mut tail = v_base.add(offset);
        #[cfg_attr(kani, kani::loop_invariant(
            crate::ub_checks::same_allocation(tail, v_base)
                && tail >= v_base.add(offset)
                && tail <= v_end
        ))]
        while tail != v_end {"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path, help="disposable smallsort.rs path")
    target = parser.parse_args().target

    source = target.read_text()
    if (
        "crate::ub_checks::same_allocation(tail, v_base)\n"
        "                && tail >= v_base.add(offset)\n"
        "                && tail <= v_end"
    ) in source:
        raise SystemExit("outer-loop invariant already injected")
    matches = source.count(ANCHOR)
    if matches != 1:
        raise SystemExit(f"expected one exact insertion_sort_shift_left anchor, found {matches}")

    target.write_text(source.replace(ANCHOR, INVARIANTS, 1))


if __name__ == "__main__":
    main()
