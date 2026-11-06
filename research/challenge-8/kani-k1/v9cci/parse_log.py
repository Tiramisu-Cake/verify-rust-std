"""parse.py LOG OUT.tsv: per-harness status/time/covers for smallsort roots in a Kani autoharness job log."""
import re
import sys

log, out = sys.argv[1], sys.argv[2]
cur, rows = {}, {}
pat_thread = re.compile(r"Z (Thread \d+): (.*)$")
for line in open(log, errors="replace"):
    m = pat_thread.search(line.rstrip("\n"))
    if not m:
        continue
    th, msg = m.groups()
    if msg.startswith("Checking harness "):
        name = msg[len("Checking harness "):].rstrip(".")
        cur[th] = name
        rows.setdefault(name, {"status": "", "vt": "", "covers": "", "failed": ""})
        continue
    name = cur.get(th)
    if not name:
        continue
    r = rows[name]
    if msg.startswith("VERIFICATION:- "):
        r["status"] = msg[len("VERIFICATION:- "):]
    elif msg.startswith("Verification Time: "):
        r["vt"] = msg[len("Verification Time: "):].rstrip("s")
    elif "cover properties satisfied" in msg:
        r["covers"] = msg.strip(" *").split(" cover")[0]
    elif re.search(r"\*\* \d+ of \d+ failed", msg):
        r["failed"] = msg.strip(" *").split(" (")[0]

ss = {k: v for k, v in rows.items() if "smallsort::verify" in k}
with open(out, "w") as f:
    f.write("harness\tstatus\tvt_s\tcovers\tfailed\n")
    for k in sorted(ss):
        v = ss[k]
        f.write(f"{k.split('verify::', 1)[1]}\t{v['status']}\t{v['vt']}\t{v['covers']}\t{v['failed']}\n")
ok = [v for v in ss.values() if v["status"].startswith("SUCCESSFUL")]
vts = sorted(((float(v["vt"]), k) for k, v in ss.items() if v["vt"]), reverse=True)
print(f"all harnesses={len(rows)} smallsort={len(ss)} success={len(ok)} sum_vt={sum(t for t, _ in vts):.0f}")
print(f">200={sum(t > 200 for t, _ in vts)} >300={sum(t > 300 for t, _ in vts)}")
for t, k in vts[:12]:
    print(f"{t:8.1f} {k.split('verify::', 1)[1]}")
bad = [k for k, v in ss.items() if not v["status"].startswith("SUCCESSFUL")]
print("non-success:", bad[:10])
