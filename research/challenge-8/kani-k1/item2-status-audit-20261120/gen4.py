#!/usr/bin/env python3
"""Fourth batch: a consumer that only sees callee SUMMARIES (havoc + assume), as stub_verified does."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import Circ, Elem, KW, T, F
from gen2 import keys, shift_rel


def build(name, n):
    c = Circ(); v = keys(c, n); ik = [e.key for e in v]
    cnt = lambda xs, x: c.count([c.eq(y, x) for y in xs])
    if name == "ins_stub_count":
        # every insert_tail call replaced by: havoc span; assume(sorted(span) && count(each old value) preserved)
        for i in range(1, n):
            old = [e.key for e in v[:i + 1]]; new = [c.inputs(KW) for _ in range(i + 1)]
            for k in range(1, i + 1): c.assert_true(-c.ult(new[k], new[k - 1]))
            for t in range(i + 1): c.assert_true(-c.neq(cnt(old, old[t]), cnt(new, old[t])))
            v = [Elem(k) for k in new] + v[i + 1:]
        ok = [e.key for e in v]
        goal = c.OR(c.ORn([c.ult(ok[k], ok[k - 1]) for k in range(1, n)]),
                    c.ORn([c.neq(cnt(ik, ik[t]), cnt(ok, ik[t])) for t in range(n)]))
    elif name == "ins_stub_thr":
        # every insert_tail call replaced by: havoc span; assume(threshold relation for the ghost q)
        q = c.inputs(KW); ind = lambda k: -c.ult(k, q)
        ii = [ind(k) for k in ik]
        for i in range(1, n):
            old = [e.key for e in v[:i + 1]]; new = [c.inputs(KW) for _ in range(i + 1)]
            rel = shift_rel(c, [ind(k) for k in old[:i]], ind(old[i]))
            for p in range(i + 1): c.assert_true(-c.XOR(ind(new[p]), rel[p]))
            v = [Elem(k) for k in new] + v[i + 1:]
        oi = [ind(e.key) for e in v]
        goal = c.OR(c.ORn([c.AND(oi[k - 1], -oi[k]) for k in range(1, n)]), c.neq(c.count(ii), c.count(oi)))
    else: raise SystemExit("unknown " + name)
    c.assert_true(goal)
    return c


if __name__ == "__main__":
    name, n, path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    build(name, n).write(path)
