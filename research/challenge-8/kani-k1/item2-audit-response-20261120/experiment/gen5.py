#!/usr/bin/env python3
"""Fifth batch: bidirectional_merge in threshold form with the loop-invariant facts supplied as lemmas (even n)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import Circ, Elem, emux, KW, T, F
from gen2 import merge_rel, keys
from gen3 import read, inc, const


def readb(c, bits, idx):
    cur = list(bits) + [bits[-1]] * ((1 << len(idx)) - len(bits))
    for b in idx:
        cur = [c.MUX(b, cur[2 * t + 1], cur[2 * t]) for t in range(len(cur) // 2)]
    return cur[0]


def build(n, inject, inv=None):
    """inject: add per-step threshold facts; inv: also add the A-or-B cursor invariant (default: same as inject)."""
    if inv is None: inv = inject
    assert n % 2 == 0
    c = Circ(); v = keys(c, n); h = n // 2; m = n - h
    q = c.inputs(KW); ind = lambda e: -c.ult(e.key, q)
    L, R = v[:h], v[h:]; Li, Ri = [ind(e) for e in L], [ind(e) for e in R]
    for xs in (Li, Ri):
        for k in range(1, len(xs)): c.assert_true(c.OR(-xs[k - 1], xs[k]))      # pre: halves q-monotone
    w = h.bit_length(); i = j = a = b = [F] * w
    out = [None] * n
    eqc = lambda bits, val: c.eq(bits, const(val, w))
    for k in range(h + 1):
        if inv:
            # forward invariant: only zeros taken so far, OR no zero left at the fronts
            A = c.AND(c.OR(eqc(i, 0), -readb(c, [F] + Li, i)), c.OR(eqc(j, 0), -readb(c, [F] + Ri, j)))
            B = c.AND(c.OR(eqc(i, h), readb(c, Li + [T], i)), c.OR(eqc(j, m), readb(c, Ri + [T], j)))
            c.assert_true(c.OR(A, B))
            # backward invariant: only ones taken so far, OR no one left at the backs
            A2 = c.AND(c.OR(eqc(a, 0), readb(c, [T] + Li[::-1], a)), c.OR(eqc(b, 0), readb(c, [T] + Ri[::-1], b)))
            B2 = c.AND(c.OR(eqc(a, h), -readb(c, Li[::-1] + [F], a)), c.OR(eqc(b, m), -readb(c, Ri[::-1] + [F], b)))
            c.assert_true(c.OR(A2, B2))
        if k == h: break
        l, r = read(c, L, i), read(c, R, j)
        is_l = -c.ult(r.key, l.key); out[k] = emux(c, is_l, l, r)
        if inject:
            c.assert_true(-c.XOR(ind(l), readb(c, Li, i))); c.assert_true(-c.XOR(ind(r), readb(c, Ri, j)))
            c.assert_true(-c.XOR(ind(out[k]), c.AND(ind(l), ind(r))))
        i, j = inc(c, i, is_l), inc(c, j, -is_l)
        l, r = read(c, L[::-1], a), read(c, R[::-1], b)
        is_l = -c.ult(r.key, l.key); out[n - 1 - k] = emux(c, is_l, r, l)
        if inject:
            c.assert_true(-c.XOR(ind(l), readb(c, Li[::-1], a))); c.assert_true(-c.XOR(ind(r), readb(c, Ri[::-1], b)))
            c.assert_true(-c.XOR(ind(out[n - 1 - k]), c.OR(ind(l), ind(r))))
        b, a = inc(c, b, is_l), inc(c, a, -is_l)
    rel = merge_rel(c, Li, Ri)
    c.assert_true(c.ORn([c.XOR(ind(out[k]), rel[k]) for k in range(n)]))
    return c


if __name__ == "__main__":
    n, mode, path = int(sys.argv[1]), sys.argv[2], sys.argv[3]   # mode: plain | step | inv
    build(n, mode in ("inv", "step"), mode == "inv").write(path)
