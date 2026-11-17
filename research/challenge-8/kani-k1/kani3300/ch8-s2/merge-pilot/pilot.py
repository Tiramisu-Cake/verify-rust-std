#!/usr/bin/env python3
"""Offline formula/transition diagnostics, never a Kani or pointer-safety proof."""
from dataclasses import dataclass

CAP = 32
DOMAIN = range(256)


def read(seq, pos):
    # Python's negative indexing must never hide a Rust sentinel dereference.
    assert 0 <= pos < len(seq), ("invalid indexed read", pos, len(seq))
    return seq[pos]


def ordered(xs):
    return all(xs[p - 1] <= xs[p] for p in range(1, len(xs)))


def counts(xs):
    result = [0] * 256
    for x in xs:
        assert type(x) is int and 0 <= x <= 255
        result[x] += 1
    return result


def ranks(src):
    # Pure snapshot formula; tie break by immutable source position.
    return tuple(sum((y, q) < (x, p) for q, y in enumerate(src))
                 for p, x in enumerate(src))


@dataclass
class State:
    src: tuple
    before: tuple
    dst: list
    initial_dst: tuple
    init: list
    base: int
    k: int = 0
    i: int = 0
    j: int = 0
    ip: int = 0
    jp: int = 0
    odd_done: bool = False
    up_done: bool = False

    @property
    def n(self):
        return len(self.src)

    @property
    def h(self):
        return self.n // 2

    def groups(self):
        h, n = self.h, self.n
        low = list(range(self.i)) + list(range(h, h + self.j))
        high = list(range(h - self.ip, h)) + list(range(n - self.jp, n))
        rem = list(range(self.i, h - self.ip)) + list(range(h + self.j, n - self.jp))
        return low, high, rem

    def bands(self):
        return list(range(self.k + int(self.odd_done or self.up_done))) + list(range(self.n - self.k, self.n))


def make_state(src, base=2):
    src = tuple(src)
    assert 2 <= len(src) <= CAP
    assert ordered(src[:len(src) // 2]) and ordered(src[len(src) // 2:])
    counts(src)
    initial = tuple(173 for _ in range(base + len(src) + 3))
    return State(src, src, list(initial), initial, [False] * len(src), base)


def endpoints(s, guarded=True):
    """C5 endpoint *membership*, not a complete order invariant."""
    if s.k == 0:
        return True  # no dst[-1], no dst[n], no source endpoints evaluated
    prefix = read(s.dst, s.base + s.k - 1)
    suffix = read(s.dst, s.base + s.n - s.k)
    if guarded:
        lo = ((s.i > 0 and prefix == read(s.src, s.i - 1)) or
              (s.j > 0 and prefix == read(s.src, s.h + s.j - 1)))
        hi = ((s.ip > 0 and suffix == read(s.src, s.h - s.ip)) or
              (s.jp > 0 and suffix == read(s.src, s.n - s.jp)))
    else:
        # Deliberately wrong: a globally in-bounds endpoint can be unconsumed.
        lo = (prefix == read(s.src, s.i - 1) or
              prefix == read(s.src, s.h + s.j - 1))
        hi = (suffix == read(s.src, s.h - s.ip) or
              suffix == read(s.src, s.n - s.jp))
    return lo and hi


def frontier_cuts(s):
    """Source-only lower/upper partition cuts used in the C5 counterfixture."""
    h, n, a = s.h, s.n, s.src
    return ((not (s.i > 0 and s.j < n - h) or read(a, s.i - 1) <= read(a, h + s.j)) and
            (not (s.j > 0 and s.i < h) or read(a, h + s.j - 1) <= read(a, s.i)) and
            (not (s.ip > 0 and s.jp < n - h) or read(a, h - s.ip) >= read(a, n - s.jp - 1)) and
            (not (s.jp > 0 and s.ip < h) or read(a, n - s.jp) >= read(a, h - s.ip - 1)))


def checks(s):
    """Pair-head invariant; odd_done extends it only for the completed odd exit."""
    n, h, k = s.n, s.h, s.k
    extra = int(s.odd_done or s.up_done)
    geometry = (2 <= n <= CAP and 0 <= k <= h and
                all(type(x) is int and x >= 0 for x in (s.i, s.j, s.ip, s.jp)) and
                s.i + s.j == k + extra and s.ip + s.jp == k and
                s.i + s.ip <= h and s.j + s.jp <= n - h and
                not (s.odd_done and s.up_done) and
                (not s.odd_done or (n % 2 == 1 and k == h)) and
                (not s.up_done or k < h))
    if not geometry:
        return {"geometry": False}
    low, high, rem = s.groups()
    bands = s.bands()
    # A failed initialization premise must not trigger reads of undefined bytes.
    if not all(s.init[p] for p in bands):
        return {"geometry": True, "frame_init": False}
    written = [read(s.dst, s.base + p) for p in bands]
    prefix = [read(s.dst, s.base + p) for p in range(k + extra)]
    suffix = [read(s.dst, s.base + p) for p in range(n - k, n)]
    remaining = [read(s.src, p) for p in rem]
    rank = ranks(s.before)
    # Snapshot rank is a specification witness, never consulted by actual_step.
    rank_cut = (all(rank[p] < k + extra for p in low) and
                all(rank[p] >= n - k for p in high) and
                all(k + extra <= rank[p] < n - k for p in rem))
    rank_output = all(any(rank[q] == p and s.before[q] == read(s.dst, s.base + p)
                          for q in range(n)) for p in bands)
    count_all = counts(s.before) == counts(written + remaining)
    consumed_counts = (counts(prefix) == counts([read(s.src, p) for p in low]) and
                       counts(suffix) == counts([read(s.src, p) for p in high]))
    # All comparisons against remaining elements require nonempty bands.
    barriers = ((not prefix or all(prefix[-1] <= x for x in remaining)) and
                (not suffix or all(x <= suffix[0] for x in remaining)) and
                (not prefix or not suffix or prefix[-1] <= suffix[0]))
    expected_init = [p in bands for p in range(n)]
    frame = (s.src == s.before and s.init == expected_init and
             all(s.dst[p] == s.initial_dst[p] for p in range(len(s.dst))
                 if not (s.base <= p < s.base + n) or p - s.base not in bands))
    return {"geometry": geometry, "frame_init": frame,
            "bands_order": ordered(prefix) and ordered(suffix),
            "barriers": barriers, "endpoints": True if extra else endpoints(s),
            "full_counts": count_all, "consumed_counts": consumed_counts,
            "rank_cut": rank_cut, "rank_output": rank_output}


def assert_invariant(s):
    result = checks(s)
    assert all(result.values()), (s, result)


def write(s, pos, value):
    assert 0 <= pos < s.n and not s.init[pos]
    s.dst[s.base + pos] = value
    s.init[pos] = True


def actual_step(s):
    """Exact integer shadow of actual up then down; both candidates always read."""
    assert not s.odd_done and not s.up_done and s.k < s.h
    assert_invariant(s)
    low, high, rem = s.groups()
    left, right = s.i, s.h + s.j
    is_l = not (read(s.src, right) < read(s.src, left))
    chosen = left if is_l else right
    assert chosen in rem, ("up selected stale front", s)
    write(s, s.k, read(s.src, chosen))
    s.i += int(is_l)
    s.j += int(not is_l)
    s.up_done = True
    assert_invariant(s)
    _, _, rem = s.groups()
    # Reverse fronts have not moved during up.
    left_rev, right_rev = s.h - 1 - s.ip, s.n - 1 - s.jp
    is_l = not (read(s.src, right_rev) < read(s.src, left_rev))
    chosen = right_rev if is_l else left_rev
    assert chosen in rem, ("down selected stale/just-consumed front", s)
    write(s, s.n - 1 - s.k, read(s.src, chosen))
    s.ip += int(not is_l)
    s.jp += int(is_l)
    s.k += 1
    s.up_done = False
    assert_invariant(s)


def odd_leftover(s, mutation=None):
    assert s.n % 2 and s.k == s.h and not s.odd_done
    _, _, rem = s.groups()
    assert len(rem) == 1
    left_nonempty = s.i < s.h - s.ip
    chosen = s.i if left_nonempty else s.h + s.j
    assert chosen == rem[0]
    if mutation == "wrong_source":
        chosen = (chosen + 1) % s.n
    if mutation != "skip_write":
        write(s, s.k, read(s.src, chosen))
    if mutation != "skip_counter":
        s.i += int(left_nonempty)
        s.j += int(not left_nonempty)
    s.odd_done = True


def post_checks(s):
    if not all(s.init):
        return {"initialized": False}  # order/count loads not defined yet
    output = s.dst[s.base:s.base + s.n]
    return {"initialized": all(s.init), "order": ordered(output),
            "full_counts": counts(output) == counts(s.before),
            "ord_panic_unreachable": s.i == s.h - s.ip and s.j == s.n - s.h - s.jp,
            "frame": all(s.dst[p] == s.initial_dst[p] for p in range(len(s.dst))
                         if p < s.base or p >= s.base + s.n) and s.src == s.before}


def run(src, base=2):
    s = make_state(src, base)
    assert_invariant(s)
    for _ in range(s.h):
        actual_step(s)
    if s.n % 2:
        odd_leftover(s)
    assert_invariant(s)
    assert all(post_checks(s).values()), (s, post_checks(s))
    return s
