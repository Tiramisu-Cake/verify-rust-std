#!/usr/bin/env python3
"""Value-level CNF models of smallsort routes + oracle variants (audit experiment).

Models (element = 8-bit key, optionally a tag):
  net9 / net13      : sort9_optimal / sort13_optimal comparator sequences from the pinned source
  net17             : sort13 on [0..13) followed by insertion of tails 13..16 (small_sort_network, N=17)
  ins8              : insertion sort from offset 1, N=8 (small_sort_network, N=8)
Oracles (the CNF asserts the NEGATION, so UNSAT == property holds for all inputs):
  sorted, countN2, count_q, ge_q, qform, qform_lemma, tag_onehot, harness (= sorted & countN2)
"""
import sys, os, json, random

HERE = os.path.dirname(os.path.abspath(__file__))

T, F = 1, -1  # var 1 is the constant TRUE


class Circ:
    def __init__(self):
        self.nv = 1
        self.cl = [[1]]
        self.cache = {}
        self.defs = {1: ("const",)}

    def new(self, d=("in",)):
        self.nv += 1
        self.defs[self.nv] = d
        return self.nv

    def AND(self, a, b):
        if a == F or b == F or a == -b: return F
        if a == T: return b
        if b == T: return a
        if a == b: return a
        k = ("and", min(a, b), max(a, b))
        if k in self.cache: return self.cache[k]
        o = self.new(k)
        self.cl += [[-o, a], [-o, b], [o, -a, -b]]
        self.cache[k] = o
        return o

    def OR(self, a, b): return -self.AND(-a, -b)

    def XOR(self, a, b):
        if a == F: return b
        if b == F: return a
        if a == T: return -b
        if b == T: return -a
        if a == b: return F
        if a == -b: return T
        neg = (a < 0) ^ (b < 0)
        a, b = abs(a), abs(b)
        k = ("xor", min(a, b), max(a, b))
        if k not in self.cache:
            o = self.new(k)
            self.cl += [[-o, a, b], [-o, -a, -b], [o, -a, b], [o, a, -b]]
            self.cache[k] = o
        o = self.cache[k]
        return -o if neg else o

    def MUX(self, s, a, b):  # s ? a : b
        if s == T: return a
        if s == F: return b
        if a == b: return a
        if a == T: return self.OR(s, b)
        if a == F: return self.AND(-s, b)
        if b == T: return self.OR(-s, a)
        if b == F: return self.AND(s, a)
        if a == -b: return self.XOR(s, b)
        k = ("mux", s, a, b)
        if k in self.cache: return self.cache[k]
        o = self.new(k)
        self.cl += [[-s, -a, o], [-s, a, -o], [s, -b, o], [s, b, -o]]
        self.cache[k] = o
        return o

    def ORn(self, xs):
        r = F
        for x in xs: r = self.OR(r, x)
        return r

    def ANDn(self, xs):
        r = T
        for x in xs: r = self.AND(r, x)
        return r

    # ---- bit-vectors, LSB first
    def inputs(self, w): return [self.new() for _ in range(w)]

    def ult(self, a, b):
        lt = F
        for x, y in zip(a, b):
            lt = self.MUX(self.XOR(x, y), self.AND(-x, y), lt)
        return lt

    def eq(self, a, b): return self.ANDn([-self.XOR(x, y) for x, y in zip(a, b)])

    def mux(self, s, a, b): return [self.MUX(s, x, y) for x, y in zip(a, b)]

    def inc_if(self, c, cond):
        """CBMC-like: cond ? c + 1 : c, width grows by one bit."""
        carry, s = T, []
        for bit in c:
            s.append(self.XOR(bit, carry)); carry = self.AND(bit, carry)
        s.append(carry)
        c2 = c + [F]
        return [self.MUX(cond, x, y) for x, y in zip(s, c2)]

    def count(self, inds):
        c = []
        for i in inds: c = self.inc_if(c, i)
        return c

    def neq(self, a, b):
        w = max(len(a), len(b)); a = a + [F] * (w - len(a)); b = b + [F] * (w - len(b))
        return self.ORn([self.XOR(x, y) for x, y in zip(a, b)])

    def assert_true(self, l): self.cl.append([l])

    def write(self, path):
        with open(path, "w") as f:
            f.write("p cnf %d %d\n" % (self.nv, len(self.cl)))
            for c in self.cl: f.write(" ".join(map(str, c)) + " 0\n")

    def evaluate(self, assign):
        """assign: dict input var -> bool. Returns list val[var]."""
        val = [None] * (self.nv + 1)
        for v in range(1, self.nv + 1):
            d = self.defs[v]
            g = lambda l: val[l] if l > 0 else (not val[-l])
            if d[0] == "const": val[v] = True
            elif d[0] == "in": val[v] = bool(assign.get(v, False))
            elif d[0] == "and": val[v] = g(d[1]) and g(d[2])
            elif d[0] == "xor": val[v] = g(d[1]) != g(d[2])
            elif d[0] == "mux": val[v] = g(d[2]) if g(d[1]) else g(d[3])
        return val


KW = 8
NETS = json.load(open(os.path.join(HERE, "nets.json")))


class Elem:
    def __init__(self, key, tag=None): self.key, self.tag = key, (tag or [])
    def bits(self): return self.key + self.tag


def emux(c, s, a, b):
    return Elem(c.mux(s, a.key, b.key), c.mux(s, a.tag, b.tag))


def run_net(c, v, pairs, log, drop=None):
    v = list(v)
    for idx, (a, b) in enumerate(pairs):
        if drop is not None and idx == drop: continue
        s = c.ult(v[b].key, v[a].key)            # is_less(v[b], v[a])
        na, nb = emux(c, s, v[b], v[a]), emux(c, s, v[a], v[b])
        log.append((v[a], v[b], na, nb))
        v[a], v[b] = na, nb
    return v


def run_insertion(c, v, start, upto=None):
    v = list(v); n = len(v) if upto is None else upto
    for i in range(start, n):
        tmp = v[i]
        sh = [None] * i; acc = T
        for j in range(i - 1, -1, -1):
            acc = c.AND(acc, c.ult(tmp.key, v[j].key)); sh[j] = acc
        new = list(v)
        new[i] = emux(c, sh[i - 1], v[i - 1], tmp)
        for p in range(i - 1, 0, -1):
            new[p] = emux(c, sh[p - 1], v[p - 1], emux(c, sh[p], tmp, v[p]))
        new[0] = emux(c, sh[0], tmp, v[0])
        v = new
    return v


def build(model, oracle, drop=None, tagmode=None):
    c = Circ()
    n = int(model[3:]) if model.startswith("ins") else {"net9": 9, "net13": 13, "net17": 17}[model]
    onehot = oracle.startswith("tag")
    ins = []
    for i in range(n):
        key = c.inputs(KW)
        tag = [T if t == i else F for t in range(n)] if onehot else []
        ins.append(Elem(key, tag))
    log = []
    if model == "net9": out = run_net(c, ins, NETS["sort9_optimal"], log, drop)
    elif model == "net13": out = run_net(c, ins, NETS["sort13_optimal"], log, drop)
    elif model == "net17":
        out = run_net(c, ins[:13], NETS["sort13_optimal"], log, drop) + ins[13:]
        out = run_insertion(c, out, 13)
    else: out = run_insertion(c, ins, 1 + (1 if drop is not None else 0))
    ik = [e.key for e in ins]; ok = [e.key for e in out]
    viol_sorted = c.ORn([c.ult(ok[i], ok[i - 1]) for i in range(1, n)])

    def countN2():
        return c.ORn([c.neq(c.count([c.eq(x, ik[i]) for x in ik]), c.count([c.eq(x, ik[i]) for x in ok])) for i in range(n)])

    if oracle == "sorted": goal = viol_sorted
    elif oracle == "countN2": goal = countN2()
    elif oracle == "harness": goal = c.OR(viol_sorted, countN2())
    elif oracle == "count_q":
        q = c.inputs(KW)
        goal = c.neq(c.count([c.eq(x, q) for x in ik]), c.count([c.eq(x, q) for x in ok]))
    elif oracle == "harness_q":
        q = c.inputs(KW)
        goal = c.OR(viol_sorted, c.neq(c.count([c.eq(x, q) for x in ik]), c.count([c.eq(x, q) for x in ok])))
    elif oracle in ("ge_q", "qform", "qform_lemma"):
        q = c.inputs(KW)
        ind = lambda x: -c.ult(x, q)             # x >= q
        ii = [ind(x) for x in ik]; oi = [ind(x) for x in ok]
        cnt = c.neq(c.count(ii), c.count(oi))
        if oracle == "ge_q": goal = cnt
        else:
            mono = c.ORn([c.AND(oi[i - 1], -oi[i]) for i in range(1, n)])
            goal = c.OR(mono, cnt)
        if oracle == "qform_lemma":
            # what stub_verified(swap_if_less) would let the caller assume for a ghost threshold q:
            # [min >= q] == [a >= q] & [b >= q],  [max >= q] == [a >= q] | [b >= q]
            for pa, pb, na, nb in log:
                A, B = ind(pa.key), ind(pb.key)
                x = c.XOR(ind(na.key), c.AND(A, B)); y = c.XOR(ind(nb.key), c.OR(A, B))
                c.assert_true(-x); c.assert_true(-y)
    elif oracle == "count_q_lemma":
        q = c.inputs(KW)
        e = lambda x: c.eq(x, q)
        goal = c.neq(c.count([e(x) for x in ik]), c.count([e(x) for x in ok]))
        for pa, pb, na, nb in log:   # pair of equality indicators is preserved as a multiset
            A, B, A2, B2 = e(pa.key), e(pb.key), e(na.key), e(nb.key)
            c.assert_true(-c.XOR(c.XOR(A, B), c.XOR(A2, B2))); c.assert_true(-c.XOR(c.AND(A, B), c.AND(A2, B2)))
    elif oracle == "tag_onehot":
        bad = []
        for e in out:
            bad.append(-c.ORn(e.tag))                                           # no tag bit
            for t1 in range(n):
                for t2 in range(t1 + 1, n): bad.append(c.AND(e.tag[t1], e.tag[t2]))  # two tag bits
                bad.append(c.AND(e.tag[t1], -c.eq(e.key, ik[t1])))              # key does not match its tag
        for t in range(n): bad.append(-c.ORn([e.tag[t] for e in out]))          # input t lost
        goal = c.ORn(bad)
    else: raise SystemExit("unknown oracle " + oracle)
    c.assert_true(goal)
    return c, ins, out


def selftest():
    """Circuit semantics vs a plain Python reference on random inputs."""
    rnd = random.Random(1)
    for model in ("net9", "net13", "net17", "ins8"):
        c, ins, out = build(model, "sorted")
        n = len(ins)
        for _ in range(200):
            xs = [rnd.choice([rnd.randrange(256), rnd.randrange(4)]) for _ in range(n)]
            asg = {}
            for e, x in zip(ins, xs):
                for b in range(KW): asg[e.key[b]] = (x >> b) & 1
            val = c.evaluate(asg)
            g = lambda l: (l == T) or (l != F and (val[l] if l > 0 else not val[-l]))
            got = [sum(g(e.key[b]) << b for b in range(KW)) for e in out]
            assert got == sorted(xs), (model, xs, got)
    print("selftest ok: circuits equal sorted() on 800 random inputs")


if __name__ == "__main__":
    if sys.argv[1] == "selftest": selftest(); sys.exit(0)
    model, oracle, path = sys.argv[1:4]
    drop = int(sys.argv[4]) if len(sys.argv) > 4 else None
    c, _, _ = build(model, oracle, drop)
    c.write(path)
    print("%s %s vars=%d clauses=%d" % (model, oracle, c.nv, len(c.cl)))
