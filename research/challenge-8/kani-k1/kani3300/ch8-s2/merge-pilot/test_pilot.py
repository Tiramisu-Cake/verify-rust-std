#!/usr/bin/env python3
"""Small deterministic diagnostics and distinguishing mutation controls."""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess

from pilot import (CAP, actual_step, assert_invariant, checks, counts, endpoints,
                   frontier_cuts, make_state, odd_leftover, ordered, post_checks,
                   ranks, read, run)

SOURCE = "99e8456d200fff1299ee5756279cddb23921dc65"
TREE = "b769b084f9982cbcb166229b29b6bd2bff136c51"
SOURCE_PATH = "library/core/src/slice/sort/shared/smallsort.rs"
BLOB = "4587a72c51325a25cca1c20138a6ee1d1aa2233f"
SOURCE_SHA256 = "45ae77ad0bb2a74cfab1aa53d5e1c48311f0b483c94eb52d96d97f680bd39651"


def source_check(repo):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args])
    assert git("rev-parse", SOURCE + "^{tree}").decode().strip() == TREE
    assert git("rev-parse", SOURCE + ":" + SOURCE_PATH).decode().strip() == BLOB
    data = git("show", SOURCE + ":" + SOURCE_PATH)
    assert hashlib.sha256(data).hexdigest() == SOURCE_SHA256
    lines = data.decode().splitlines()
    sites = json.loads(Path(__file__).with_name("source-map.json").read_text())
    for site in sites["sites"]:
        assert lines[site["line"] - 1].strip() == site["text"], site
    return {"commit": SOURCE, "tree": TREE, "blob": BLOB,
            "sha256": SOURCE_SHA256, "exact_site_checks": len(sites["sites"])}


def rejected_read(action):
    try:
        action()
    except AssertionError:
        return True
    raise AssertionError("expected invalid indexed read was accepted")


def negative_controls():
    result = {}
    # Exact section 6 abstract state: not an actual reachable trace.
    trap = make_state([1, 9, 2, 10])
    trap.k = trap.i = trap.jp = 1
    trap.dst[trap.base], trap.dst[trap.base + 3] = 9, 2
    trap.init[0] = trap.init[3] = True
    _, _, rem = trap.groups()
    weak_query = (sum(x == 0 for x in trap.before) ==
                  sum(x == 0 for x in [9, 2] + [trap.src[p] for p in rem]))
    assert frontier_cuts(trap) and ordered([9]) and ordered([2])
    assert endpoints(trap, guarded=False) and weak_query
    strong = checks(trap)
    assert not strong["endpoints"] and not strong["full_counts"]
    assert not strong["rank_output"] and not strong["barriers"]
    result["C5_len4_probe0"] = {"weak_accepts": True,
        "rejects": [name for name, ok in strong.items() if not ok]}

    # k0 must not even evaluate an endpoint; unguarded reverse exhaustion is invalid.
    class NoReads:
        def __len__(self):
            return 4
        def __getitem__(self, pos):
            raise AssertionError("k0 endpoint read")
    zero = make_state([1, 9, 2, 10])
    zero.src = zero.dst = NoReads()
    assert endpoints(zero)
    result["unguarded_k0_read"] = {"caught": rejected_read(lambda: read([1, 2], -1))}
    # An actual exhausted reverse left front is -1: never dereference it after exit.
    sentinel = run([9, 10, 1, 2])
    assert sentinel.h - 1 - sentinel.ip == -1
    result["unguarded_reverse_sentinel"] = {"caught": rejected_read(
        lambda: read(sentinel.src, sentinel.h - 1 - sentinel.ip))}

    # Poison unwritten slots: any byte comparison/count before a write must fail.
    uninit = make_state([1, 9, 2, 10])
    for p in range(uninit.n):
        uninit.dst[uninit.base + p] = object()
    uninit.initial_dst = tuple(uninit.dst)
    assert_invariant(uninit)
    for _ in range(uninit.h):
        actual_step(uninit)
    assert all(post_checks(uninit).values())
    result["unwritten_poison_definedness"] = {"guarded_predicates_pass": True}

    good = run([1, 9, 2, 10])
    lost = copy.deepcopy(good)
    lost.dst[lost.base + 2] = 8  # sorted, but 9 lost and 8 invented; probe0 sees neither.
    cp = post_checks(lost)
    assert cp["order"] and not cp["full_counts"]
    result["lost_value_weak_order_probe0"] = {"order_accepts": True,
        "probe0_accepts": 0 not in lost.before and 0 not in lost.dst[lost.base:lost.base + 4],
        "rejects": ["full_counts", "rank_output"]}
    assert not checks(lost)["rank_output"]
    dup = copy.deepcopy(good)
    dup.dst[dup.base + 1] = 1
    assert post_checks(dup)["order"] and not post_checks(dup)["full_counts"]
    result["duplicate_value"] = {"order_accepts": True, "rejects": ["full_counts"]}
    swapped = copy.deepcopy(good)
    swapped.dst[swapped.base], swapped.dst[swapped.base + 1] = 2, 1
    assert post_checks(swapped)["full_counts"] and not post_checks(swapped)["order"]
    result["weak_count_without_order"] = {"full_counts_accepts": True, "rejects": ["order"]}

    frame = copy.deepcopy(good)
    frame.dst[frame.base - 1] ^= 1
    assert post_checks(frame)["order"] and post_checks(frame)["full_counts"]
    assert not checks(frame)["frame_init"] and not post_checks(frame)["frame"]
    result["wrong_frame"] = {"semantic_posts_accept": True, "rejects": ["frame_init", "frame"]}
    source = copy.deepcopy(good)
    source.src = (0,) + source.src[1:]
    assert not checks(source)["frame_init"]
    result["source_clobber"] = {"rejects": ["frame_init"]}

    for mutation in ("skip_write", "skip_counter", "wrong_source"):
        odd = make_state([1, 4, 2, 3, 5])
        for _ in range(odd.h):
            actual_step(odd)
        odd_leftover(odd, mutation)
        cp = post_checks(odd)
        assert not all(cp.values())
        result["odd_" + mutation] = {"rejects": [name for name, ok in cp.items() if not ok]}

    # Breaking down's tie rule duplicates the last token when halves are all equal.
    tie = make_state([7, 7])
    tie.k = tie.i = tie.ip = 1
    tie.dst[tie.base:tie.base + 2] = [7, 7]
    tie.init[:] = [True, True]
    assert post_checks(tie)["order"] and post_checks(tie)["full_counts"]
    assert not checks(tie)["geometry"] and not post_checks(tie)["ord_panic_unreachable"]
    result["wrong_down_tie"] = {"value_posts_accept": True,
        "rejects": ["geometry", "ord_panic_unreachable"]}
    return result


def geometry_diagnostics():
    pairs = []
    for n in range(16, CAP + 1):
        for src, dst in ((n, 0), (n + 8, n // 2)):
            assert src + 8 <= n + 16 and dst + 8 <= n + 16
            assert dst + 8 <= src or src + 8 <= dst
            pairs.append((src, dst))
    assert len(pairs) == len(set(pairs)) == 34
    def interval_disjoint(s, d, n):
        return s + n <= d or d + n <= s
    assert not interval_disjoint(8, 12, 8)  # wrong overlap, numeric geometry only
    assert interval_disjoint(8, 0, 8)       # adjacent regions are allowed
    return {"sort8_distinct_same_allocation_pairs": len(pairs),
            "overlap_negative_rejected": True, "adjacent_positive_accepted": True,
            "pointer_proof": "NOT_RUN"}


def diagnostics():
    small, cap, transitions, exhausted, odd_left, odd_right = 0, 0, 0, 0, 0, 0
    for n in range(2, 9):
        h = n // 2
        for a in itertools.combinations_with_replacement((0, 1, 255), h):
            for b in itertools.combinations_with_replacement((0, 1, 255), n - h):
                src = a + b
                # Rank bijection diagnostic, not an assumed axiom in a future proof.
                assert sorted(ranks(src)) == list(range(n))
                s = make_state(src)
                assert_invariant(s)
                for _ in range(h):
                    if s.i + s.ip == h or s.j + s.jp == n - h:
                        exhausted += 1
                    actual_step(s)
                    transitions += 1
                if n % 2:
                    odd_left += s.i < h - s.ip
                    odd_right += not (s.i < h - s.ip)
                    odd_leftover(s)
                assert_invariant(s)
                assert all(post_checks(s).values())
                small += 1
    rng = random.Random(9856043)
    for n in range(2, CAP + 1):
        h = n // 2
        fixtures = ([0] * n, [255] * n, [0] * h + [255] * (n - h),
                    [255] * h + [0] * (n - h))
        random_fixtures = [sorted(rng.randrange(256) for _ in range(h)) +
                           sorted(rng.randrange(256) for _ in range(n - h)) for _ in range(8)]
        for src in list(fixtures) + random_fixtures:
            assert sorted(ranks(src)) == list(range(n))
            run(src, base=n % 3)
            cap += 1
    assert exhausted and odd_left and odd_right
    return {"small_alphabet_sorted_half_inputs": small,
            "small_alphabet_pair_transitions": transitions,
            "live_loop_heads_with_exhausted_half": exhausted,
            "odd_left_cases": odd_left, "odd_right_cases": odd_right,
            "CAP32_fixtures_all_lengths": cap,
            "negative_controls": negative_controls()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-repo", type=Path, required=True)
    args = parser.parse_args()
    receipt = {"schema": "ch8-s2-merge-pilot-validation-v1", "task": "task9856043dab21de8346b68196fa91929b96331293",
               "source": source_check(args.source_repo), "diagnostics": diagnostics(),
               "geometry": geometry_diagnostics(),
               "result": "PASS_DIAGNOSTIC_ONLY", "proof_credit": "NONE",
               "Kani": "NOT_RUN", "S3_qualification": "NONE", "CI_dispatches": 0}
    package = Path(__file__).parent
    receipt["package_sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
        for name in ("pilot.py", "test_pilot.py", "source-map.json", "INVARIANT.md",
                     "HANDOFF.md", "VALIDATION.md")}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
