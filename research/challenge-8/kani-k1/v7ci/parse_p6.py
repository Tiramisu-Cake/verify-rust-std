import re, sys, csv
# usage: parse_p6.py out.tsv job_id:os:partition:logpath ...
rx = re.compile(r'^\S+Z Thread (\d+): (.*)$')
rows = []
for spec in sys.argv[2:]:
    job, os_, part, path = spec.split(':', 3)
    cur = {}
    with open(path, errors='replace') as f:
        for line in f:
            m = rx.match(line.rstrip('\n'))
            if not m:
                continue
            t, msg = m.groups()
            if msg.startswith('Checking harness '):
                cur[t] = {'h': msg[len('Checking harness '):].rstrip('.'), 'st': None}
            elif msg.startswith('VERIFICATION:- ') and t in cur:
                cur[t]['st'] = msg[len('VERIFICATION:- '):].strip()
            elif msg.startswith('Verification Time: ') and t in cur:
                vt = msg[len('Verification Time: '):].rstrip('s')
                c = cur.pop(t)
                rows.append((c['h'], os_, part, job, c['st'], vt))
with open(sys.argv[1], 'w', newline='') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['harness','os','partition','job','status','vt_s']); w.writerows(rows)
print(len(rows), 'rows')
