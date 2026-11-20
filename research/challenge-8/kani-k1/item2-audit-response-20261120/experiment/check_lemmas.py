"""Soundness test of every injected lemma: on random inputs that satisfy the preconditions,
all asserted facts except the final (negated) goal must evaluate to true."""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen, gen2, gen3, gen4, gen5
from gen import Circ, KW, T, F

units = []
orig = Circ.assert_true
def rec(self, l): units.append(l); orig(self, l)
Circ.assert_true = rec
rnd = random.Random(11)

def run(label, builder, sampler, trials=400):
    units.clear(); c = builder()
    asserted, goal = units[:-1], units[-1]
    ins = [v for v, d in c.defs.items() if d[0] == "in"]
    bad = 0; goal_true = 0
    for _ in range(trials):
        bits = sampler(len(ins))
        val = c.evaluate(dict(zip(ins, bits)))
        g = lambda l: (l == T) or (l != F and (val[l] if l > 0 else not val[-l]))
        if not all(g(l) for l in asserted): bad += 1
        if g(goal): goal_true += 1
    print("%-34s lemmas/preconditions asserted=%4d  violated on %d of %d random inputs; goal (violation) true on %d" % (label, len(asserted), bad, trials, goal_true))

def bytes_bits(xs): return [(x >> b) & 1 for x in xs for b in range(KW)]
def small(): return rnd.choice([rnd.randrange(256), rnd.randrange(4), 255])

# inputs are allocated in order: n keys (8 bits each) then q (8 bits)   [gen/gen2 route models]
def free_keys_then_q(n): return lambda k: bytes_bits([small() for _ in range(n)] + [small()])[:k]
run("net13 qform_lemma", lambda: gen.build("net13", "qform_lemma")[0], free_keys_then_q(13))
run("net13 count_q_lemma", lambda: gen.build("net13", "count_q_lemma")[0], free_keys_then_q(13))
run("ins16 qform_lemma", lambda: gen2.build("ins_qform_lemma", 16), free_keys_then_q(16))
run("net17 qform_lemma", lambda: gen2.build("net17_qform_lemma", 17), free_keys_then_q(17))

def qmono_halves(n, sizes):
    def s(k):
        q = small(); xs = []
        for sz in sizes:
            z = rnd.randrange(sz + 1)
            lo = [rnd.randrange(q) for _ in range(z)] if q > 0 else []
            hi = [rnd.randrange(q, 256) for _ in range(sz - len(lo))]
            xs += lo + hi
        return bytes_bits(xs + [q])[:k]
    return s
run("ins_leaf_qform n=17 (prefix 16)", lambda: gen2.build("ins_leaf_qform", 17), qmono_halves(17, [16, 1]))
run("merge_B n=16", lambda: gen3.build("merge_B", 16)[0], qmono_halves(16, [8, 8]))
run("merge_thr n=32 + invariant", lambda: gen5.build(32, True), qmono_halves(32, [16, 16]), trials=300)
run("merge_thr n=16 + invariant", lambda: gen5.build(16, True), qmono_halves(16, [8, 8]))
