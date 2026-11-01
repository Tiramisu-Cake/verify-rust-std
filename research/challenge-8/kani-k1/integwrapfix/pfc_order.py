# Static check for the kani list ordering bug: an ordinary proof_for_contract harness must come after its
# target function in crate item order (module declaration order, then position in file).
import re,sys,os
root=sys.argv[1]  # .../smallsort
order=[]  # (file, line) sequence approximating DefIndex order
def walk(path):
    order.append(path)
    src=open(path).read().split('\n')
    base=os.path.splitext(path)[0]
    for i,l in enumerate(src):
        m=re.match(r'^\s*(?:pub(?:\([\w ]+\))? )?mod (\w+);',l)
        if m and not (i>0 and 'cfg(any())' in src[i-1]):
            sub=os.path.join(base,m.group(1)+'.rs')
            order.append((path,i+1,'mod',sub)); walk(sub)
walk(root+'.rs')
pos={}; k=0; fns={}; pfcs=[]
seq=[]
def scan(path,start_idx):
    pass
# flatten: assign increasing index to each fn def / harness in visiting order
idx=0
def visit(path):
    global idx
    src=open(path).read().split('\n'); base=os.path.splitext(path)[0]
    for i,l in enumerate(src):
        idx+=1
        prev=src[i-3:i]
        gated=any('cfg(any())' in p or 'kani_smallsort_controls' in p for p in prev if p.strip().startswith('#['))
        m=re.match(r'^\s*(?:pub(?:\([\w ]+\))? )?mod (\w+);',l)
        if m and not (i>0 and 'cfg(any())' in src[i-1]):
            visit(os.path.join(base,m.group(1)+'.rs')); continue
        m=re.match(r'^\s*(?:pub(?:\(\w+\))? )?(?:unsafe )?fn (\w+)',l)
        if m: fns.setdefault(m.group(1),[]).append((idx,path,i+1))
        m=re.search(r'proof_for_contract\(([\w:]+)\)',l)
        if m and not gated: pfcs.append((idx,path,i+1,m.group(1).split('::')[-1]))
visit(root+'.rs')
bad=0
for idx_,p,ln,t in pfcs:
    d=fns.get(t)
    if not d: print('NO TARGET',p,ln,t); bad+=1; continue
    if min(x[0] for x in d)>idx_: print('BEFORE TARGET',os.path.relpath(p,root),ln,t); bad+=1
print('ordinary pfc sites',len(pfcs),'bad',bad)
