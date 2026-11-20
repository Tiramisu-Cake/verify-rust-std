import os, random, subprocess, itertools, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen
rnd = random.Random(7)
bad = 0
# 1) random 3-SAT near threshold vs brute force
for t in range(300):
    n = rnd.randrange(5, 16); m = int(n * rnd.uniform(3.5, 5.0))
    cls = [[rnd.choice([-1, 1]) * v for v in rnd.sample(range(1, n + 1), 3)] for _ in range(m)]
    with open(os.path.join(HERE, "t.cnf"), "w") as f:
        f.write("p cnf %d %d\n" % (n, m)); [f.write(" ".join(map(str, c)) + " 0\n") for c in cls]
    r = subprocess.run([os.path.join(HERE, "cdcl"), os.path.join(HERE, "t.cnf"), "100000", "20", os.path.join(HERE, "t.model")], capture_output=True, text=True)
    sat = any(all(any((l > 0) == bits[abs(l) - 1] for l in c) for c in cls) for bits in itertools.product([False, True], repeat=n))
    got = r.stdout.split()[0]
    if got != ("SATISFIABLE" if sat else "UNSATISFIABLE"): bad += 1
    elif sat:
        mdl = [int(x) for x in open(os.path.join(HERE, "t.model"))]
        if not all(any(l in mdl for l in c) for c in cls): bad += 1
print("random 3-SAT vs brute force: 300 cases, mismatches =", bad)
# 2) broken networks must give SAT with a genuine counterexample
for model, oracle, drop in (("net9", "sorted", 24), ("net13", "sorted", 44), ("net13", "harness", 10), ("net13", "qform", 3), ("ins8", "sorted", 1)):
    c, ins, out = gen.build(model, oracle, drop)
    c.write(os.path.join(HERE, "t.cnf"))
    r = subprocess.run([os.path.join(HERE, "cdcl"), os.path.join(HERE, "t.cnf"), "2000000", "60", os.path.join(HERE, "t.model")], capture_output=True, text=True)
    res = r.stdout.split()[0]
    ok = None
    if res == "SATISFIABLE":
        mdl = {abs(int(x)): int(x) > 0 for x in open(os.path.join(HERE, "t.model"))}
        val = c.evaluate({v: mdl[v] for v, d in c.defs.items() if d[0] == "in"})
        g = lambda l: (l == gen.T) or (l != gen.F and (val[l] if l > 0 else not val[-l]))
        o = [sum(g(e.key[b]) << b for b in range(8)) for e in out]
        ok = any(o[i] < o[i - 1] for i in range(1, len(o)))
    print(model, oracle, "drop", drop, "->", r.stdout.strip(), "| output really unsorted:", ok)
