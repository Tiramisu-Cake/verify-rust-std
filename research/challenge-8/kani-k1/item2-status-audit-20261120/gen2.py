#!/usr/bin/env python3
"""Second batch of audit experiments: threshold-form (0-1) contracts for insertion, merge and whole routes."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import Circ, Elem, emux, run_net, NETS, KW, T, F


def ins_step(c, v, i):
    """insert_tail on v[0..=i] (value level); returns new list."""
    tmp = v[i]; sh = [None] * i; acc = T
    for j in range(i - 1, -1, -1):
        acc = c.AND(acc, c.ult(tmp.key, v[j].key)); sh[j] = acc
    new = list(v)
    new[i] = emux(c, sh[i - 1], v[i - 1], tmp)
    for p in range(i - 1, 0, -1):
        new[p] = emux(c, sh[p - 1], v[p - 1], emux(c, sh[p], tmp, v[p]))
    new[0] = emux(c, sh[0], tmp, v[0])
    return new


def shift_rel(c, pre_ind, t):
    """threshold-form post of insert_tail: tail>=q keeps positions, tail<q shifts the prefix right by one."""
    i = len(pre_ind)
    return [c.MUX(t, pre_ind[p] if p < i else T, F if p == 0 else pre_ind[p - 1]) for p in range(i + 1)]


def thr(c, xs):
    """unary counter: res[j] == 'at least j of xs are 1', j = 0..len(xs)."""
    s = [T] + [F] * len(xs)
    for x in xs:
        s = [T] + [c.OR(s[j], c.AND(x, s[j - 1])) for j in range(1, len(xs) + 1)]
    return s


def sorted_ind(c, xs):
    n = len(xs); s = thr(c, xs)
    return [s[n - k] for k in range(n)]          # out[k] = 1 iff at least n-k ones


def merge_rel(c, L, R):
    """threshold-form post of a merge of two q-monotone halves: out[k] = 1 iff zeros(L)+zeros(R) <= k."""
    h, m = len(L), len(R)
    zl = lambda i: T if i == h else L[i]       # zeros(L) <= i
    zr = lambda j: T if j == m else R[j]
    return [c.ORn([c.AND(zl(i), zr(k - i)) for i in range(max(0, k - m), min(h, k) + 1)]) for k in range(h + m)]


def keys(c, n): return [Elem(c.inputs(KW)) for _ in range(n)]


def build(name, n):
    c = Circ()
    if name in ("ins_qform_lemma", "net17_qform_lemma", "ins_qform"):
        # whole insertion route (fallback / network without merge) in threshold form with per-call lemmas
        v = keys(c, n); q = c.inputs(KW); ind = lambda e: -c.ult(e.key, q)
        ii = [ind(e) for e in v]
        start = 1
        if name.startswith("net17"):
            log = []; v = run_net(c, v[:13], NETS["sort13_optimal"], log) + v[13:]; start = 13
            for pa, pb, na, nb in log:
                A, B = ind(pa), ind(pb)
                c.assert_true(-c.XOR(ind(na), c.AND(A, B))); c.assert_true(-c.XOR(ind(nb), c.OR(A, B)))
        for i in range(start, n):
            new = ins_step(c, v, i)
            if name != "ins_qform":
                rel = shift_rel(c, [ind(e) for e in v[:i]], ind(v[i]))
                for p in range(i + 1): c.assert_true(-c.XOR(ind(new[p]), rel[p]))
            v = new
        oi = [ind(e) for e in v]
        goal = c.OR(c.ORn([c.AND(oi[k - 1], -oi[k]) for k in range(1, n)]), c.neq(c.count(ii), c.count(oi)))
    elif name == "ins_leaf_qform":
        # leaf obligation: real insert_tail body on prefix of n-1 elements, pre = prefix q-monotone only
        v = keys(c, n); q = c.inputs(KW); ind = lambda e: -c.ult(e.key, q)
        pre = [ind(e) for e in v[:n - 1]]
        for k in range(1, n - 1): c.assert_true(c.OR(-pre[k - 1], pre[k]))
        new = ins_step(c, v, n - 1); rel = shift_rel(c, pre, ind(v[n - 1]))
        goal = c.ORn([c.XOR(ind(new[p]), rel[p]) for p in range(n)])
    elif name == "ins_leaf_std":
        # same leaf with the current full-value contract: prefix sorted => sorted + count per input value
        v = keys(c, n)
        for k in range(1, n - 1): c.assert_true(-c.ult(v[k].key, v[k - 1].key))
        new = ins_step(c, v, n - 1); ik = [e.key for e in v]; ok = [e.key for e in new]
        goal = c.OR(c.ORn([c.ult(ok[k], ok[k - 1]) for k in range(1, n)]),
                    c.ORn([c.neq(c.count([c.eq(x, ik[i]) for x in ik]), c.count([c.eq(x, ik[i]) for x in ok])) for i in range(n)]))
    elif name in ("general_ind_mono", "general_ind_ostat", "network_ind_mono", "network_ind_ostat"):
        # whole route with every callee replaced by its threshold-form summary: pure indicator space
        x = c.inputs(n); h = n // 2
        def half(xs):
            if name.startswith("general"):
                pres = 8 if len(xs) >= 8 and n >= 16 else (4 if n >= 8 else 1)
            else:
                pres = 13 if len(xs) >= 13 else (9 if len(xs) >= 9 else 1)
            cur = sorted_ind(c, xs[:pres])
            for i in range(pres, len(xs)): cur = shift_rel(c, cur, xs[i])
            return cur
        if name.startswith("network") and n < 18: out = half(x)
        else: out = merge_rel(c, half(x[:h]), half(x[h:]))
        if name.endswith("mono"):
            goal = c.OR(c.ORn([c.AND(out[k - 1], -out[k]) for k in range(1, n)]), c.neq(c.count(x), c.count(out)))
        else:
            spec = sorted_ind(c, x)
            goal = c.ORn([c.XOR(out[k], spec[k]) for k in range(n)])
    else: raise SystemExit("unknown " + name)
    c.assert_true(goal)
    return c


if __name__ == "__main__":
    name, n, path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    c = build(name, n); c.write(path)
    print("%s n=%d vars=%d clauses=%d" % (name, n, c.nv, len(c.cl)))
