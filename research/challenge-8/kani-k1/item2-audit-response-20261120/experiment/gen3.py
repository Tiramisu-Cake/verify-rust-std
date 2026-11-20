#!/usr/bin/env python3
"""Third batch: value-level model of bidirectional_merge (monolithic leaf) under three contract forms."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import Circ, Elem, emux, KW, T, F
from gen2 import merge_rel, keys, ins_step


def read(c, arr, idx):
    cur = list(arr) + [arr[-1]] * ((1 << len(idx)) - len(arr))
    for b in idx:
        cur = [emux(c, b, cur[2 * t + 1], cur[2 * t]) for t in range(len(cur) // 2)]
    return cur[0]


def inc(c, bits, cond):
    out, carry = [], cond
    for b in bits:
        out.append(c.XOR(b, carry)); carry = c.AND(b, carry)
    return out


def add(c, a, b):
    out, carry = [], F
    for x, y in zip(a, b):
        s = c.XOR(x, y); out.append(c.XOR(s, carry)); carry = c.OR(c.AND(x, y), c.AND(s, carry))
    return out + [carry]


def const(v, w): return [T if (v >> k) & 1 else F for k in range(w)]


def merge(c, v):
    """returns (out, panic) following bidirectional_merge / merge_up / merge_down."""
    n = len(v); h = n // 2; m = n - h
    L, R = v[:h], v[h:]; Lr, Rr = L[::-1], R[::-1]
    w = max(1, (h).bit_length())
    i = j = a = b = [F] * w
    out = [None] * n
    for k in range(h):
        l, r = read(c, L, i), read(c, R, j)
        is_l = -c.ult(r.key, l.key)                      # !is_less(right, left)
        out[k] = emux(c, is_l, l, r)
        i, j = inc(c, i, is_l), inc(c, j, -is_l)
        l, r = read(c, Lr, a), read(c, Rr, b)
        is_l = -c.ult(r.key, l.key)
        out[n - 1 - k] = emux(c, is_l, r, l)              # take right when !(right < left)
        b, a = inc(c, b, is_l), inc(c, a, -is_l)
    ia = add(c, i, a)                                    # left consumed from both ends
    jb = add(c, j, b)
    W = len(ia)
    if n % 2:
        left_nonempty = c.ult(ia, const(h, W))           # left < left_end  <=>  i + a < h
        out[h] = emux(c, left_nonempty, read(c, L, i), read(c, R, j))
        ia = add(c, ia, [left_nonempty] + [F] * (W - 1))[:W]
        jb = add(c, jb, [-left_nonempty] + [F] * (W - 1))[:W]
    panic = c.OR(-c.eq(ia, const(h, W)), -c.eq(jb, const(m, W)))
    return out, panic


def build(name, n):
    c = Circ(); v = keys(c, n); h = n // 2
    full_sorted = lambda xs: [-c.ult(xs[k].key, xs[k - 1].key) for k in range(1, len(xs))]
    if name in ("merge_std", "merge_A", "merge_A_sorted", "merge_A_nopanic"):
        for l in full_sorted(v[:h]) + full_sorted(v[h:]): c.assert_true(l)
        out, panic = merge(c, v)
        ik = [e.key for e in v]; ok = [e.key for e in out]
        uns = c.ORn([c.ult(ok[k], ok[k - 1]) for k in range(1, n)])
        if name == "merge_A": goal = c.OR(panic, uns)
        elif name == "merge_A_sorted": goal = uns
        elif name == "merge_A_nopanic": goal = panic
        else:
            cnt = c.ORn([c.neq(c.count([c.eq(x, ik[t]) for x in ik]), c.count([c.eq(x, ik[t]) for x in ok])) for t in range(n)])
            goal = c.ORn([panic, uns, cnt])
    elif name == "merge_B":
        q = c.inputs(KW); ind = lambda e: -c.ult(e.key, q)
        Li, Ri = [ind(e) for e in v[:h]], [ind(e) for e in v[h:]]
        for xs in (Li, Ri):
            for k in range(1, len(xs)): c.assert_true(c.OR(-xs[k - 1], xs[k]))
        out, panic = merge(c, v); rel = merge_rel(c, Li, Ri)
        goal = c.AND(-panic if n % 2 else T, c.ORn([c.XOR(ind(out[k]), rel[k]) for k in range(n)]))
    elif name == "ins_leaf_A":
        for l in full_sorted(v[:n - 1]): c.assert_true(l)
        new = ins_step(c, v, n - 1)
        goal = c.ORn([c.ult(new[k].key, new[k - 1].key) for k in range(1, n)])
    else: raise SystemExit("unknown " + name)
    c.assert_true(goal)
    return c, v


def selftest():
    import random
    rnd = random.Random(5)
    for n in (2, 3, 8, 9, 16, 17, 32):
        c = Circ(); v = keys(c, n); out, panic = merge(c, v); h = n // 2
        for _ in range(150):
            xs = sorted(rnd.choice([rnd.randrange(256), rnd.randrange(3)]) for _ in range(h)) + sorted(rnd.choice([rnd.randrange(256), rnd.randrange(3)]) for _ in range(n - h))
            asg = {}
            for e, x in zip(v, xs):
                for b in range(KW): asg[e.key[b]] = (x >> b) & 1
            val = c.evaluate(asg)
            g = lambda l: (l == T) or (l != F and (val[l] if l > 0 else not val[-l]))
            got = [sum(g(e.key[b]) << b for b in range(KW)) for e in out]
            assert got == sorted(xs) and not g(panic), (n, xs, got, g(panic))
    print("merge selftest ok: model == sorted(), no panic, on sorted halves (n=2,3,8,9,16,17,32)")


if __name__ == "__main__":
    if sys.argv[1] == "selftest": selftest(); sys.exit(0)
    name, n, path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    c, _ = build(name, n); c.write(path)
