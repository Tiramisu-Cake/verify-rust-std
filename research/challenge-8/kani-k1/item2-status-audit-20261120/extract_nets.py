#!/usr/bin/env python3
"""Extract the sort9_optimal / sort13_optimal comparator sequences from smallsort.rs and check them on all 0-1 inputs.
usage: extract_nets.py path/to/smallsort.rs   (writes nets.json next to this script)"""
import os, re, sys, json
src = open(sys.argv[1]).read(); nets = {}
for name in ("sort9_optimal", "sort13_optimal"):
    i = src.index("fn " + name); j = src.index("\n}\n", i)
    nets[name] = [(int(a), int(b)) for a, b in re.findall(r"swap_if_less\(v_base,\s*(\d+),\s*(\d+),\s*is_less\)", src[i:j])]
json.dump(nets, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "nets.json"), "w"))
for name, n in (("sort9_optimal", 9), ("sort13_optimal", 13)):
    ok = True
    for m in range(1 << n):
        v = [(m >> k) & 1 for k in range(n)]; o = list(v)
        for a, b in nets[name]:
            if o[b] < o[a]: o[a], o[b] = o[b], o[a]
        ok &= all(o[k] <= o[k + 1] for k in range(n - 1)) and sum(o) == sum(v)
    print(name, len(nets[name]), "comparators; sorts all", 1 << n, "0-1 inputs:", ok)
