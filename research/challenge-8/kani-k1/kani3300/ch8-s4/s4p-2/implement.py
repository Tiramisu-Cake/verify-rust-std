"""Offline S4P2 sibling construction. Never invokes native tools or dispatch."""
from pathlib import Path
import hashlib,json,re,subprocess
MAIN=Path('/root/verify-rust-std-kani3300-g0')
BASE=MAIN/'research/challenge-8/kani-k1'
OUT=BASE/'kani3300/ch8-s4/s4p-2'
SOURCE=Path('/root/verify-rust-std-ch8-s4p-2-w13')
CONTROL=Path('/root/kani-ch8-s4p-2-control-w13')
HERE=CONTROL/'ch8-s1-control'
OLD=Path('/root/kani-ch8-s4p-1-r1-control-w13')/'ch8-s1-control'
TASK='bf3aba53618b759a11d3ff277e88ba66530ec708'
def put(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n')
def digest(data):return hashlib.sha256(data).hexdigest()
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
leaf='library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_network_partition.rs'
verify='library/core/src/slice/sort/shared/smallsort/verify.rs'
oldleaf=leaf.replace('sorting_s4_network_partition','sorting_s4_partition')
def main():
    text=(SOURCE/oldleaf).read_text()
    header=text[:text.index('// Checker-only')].replace('//! S4 full-byte length blocks: finite normal-return candidates, no proof credit.','//! S4P2 exact network partitions: finite normal-return candidates, no proof credit.').replace('use super::super::{small_sort_fallback, small_sort_network};','use super::super::small_sort_network;').replace('use crate::{kani, cell::Cell};','use crate::kani;')
    begin=text.rindex('#[kani::proof]',0,text.index('fn s4p_network_b01_n00_02_fullbyte'))
    end=text.index('#[kani::proof]',text.index('fn s4p_network_b01_n00_02_fullbyte'))
    template=text[begin:end]
    chunks=[]
    for lo,hi in ((2,2),(3,3),(4,4),(0,1)):
        suffix=f'n{lo:02}' if lo==hi else 'n00_01'
        name='s4p2_network_b01_'+suffix+'_fullbyte'
        prefix='S4P2_N_'+(f'{lo:02}' if lo==hi else '00_01')
        chunk=template.replace('s4p_network_b01_n00_02_fullbyte',name).replace('S4P_N_00_02',prefix)
        chunk=chunk.replace('kani::assume(0 <= n && n <= 2);',f'kani::assume({lo} <= n && n <= {hi});')
        start=chunk.index('    kani::cover(n == 0,')
        chunk=chunk[:start]+''.join(f'    kani::cover(n == {n}, "{prefix}_N{n:02}");\n' for n in range(lo,hi+1))+('' if hi==1 else ''.join([
            f'    kani::cover(n >= 2 && bytes[1] > bytes[n], "{prefix}_UNSORTED");\n',
            f'    kani::cover(n >= 2 && bytes[1] == bytes[n], "{prefix}_DUPLICATE");\n',
            f'    kani::cover(n >= 2 && v[1] < v[n], "{prefix}_NONCONSTANT");\n',
            f'    kani::cover(n == {hi} && descending(&bytes[1..{hi+1}]), "{prefix}_MAX_DESCENDING");\n']))+f'    kani::cover(true, "{prefix}_USEFUL_RETURN");\n}}\n\n'
        chunks.append(chunk)
    (SOURCE/leaf).write_text(header+''.join(chunks))
    original=subprocess.check_output(['git','-C',str(SOURCE),'show','985062ebad90cee1e2846b1648cd6a8624d146f6:'+verify]).decode()
    (SOURCE/verify).write_text(original+'\n// S4P2 exact network singletons and N0..1; no assumed replacements.\n#[cfg(all(kani, kani_smallsort_sorting, kani_smallsort_s2_assumed, kani_smallsort_s3_leaf, kani_smallsort_s4_partition))]\npub(super) mod sorting_s4_network_partition;\n')
    for suffix in ('cfg_pfc','contract_stacks','ordinary_contracts','lexical_bindings','policy','profile','campaign','package'):
        data=(OLD/('s4p_'+suffix+'.py')).read_text().replace('s4p_', 's4p2_').replace('ch8-s4p-1','ch8-s4p-2').replace('S4P-SOURCE','S4P2-SOURCE')
        (HERE/('s4p2_'+suffix+'.py')).write_text(data)
    for suffix in ('cfg_pfc','lexical_bindings'):
        path=HERE/('s4p2_'+suffix+'.py');data=path.read_text()
        data=data.replace("'sorting_bridge1', 'sorting_s4_partition')","'sorting_bridge1', 'sorting_s4_partition', 'sorting_s4_network_partition')")
        data=data.replace("(c.VERIFY, 'sorting_s4_partition'),", "(c.VERIFY, 'sorting_s4_partition'), (c.VERIFY, 'sorting_s4_network_partition'),")
        data=data.replace("'sorting_bridge1','sorting_s4_partition')", "'sorting_bridge1','sorting_s4_partition','sorting_s4_network_partition')")
        if suffix=='lexical_bindings':
            anchor="    byname = {r['function']:r for r in records}"
            data=data.replace(anchor,"    network = c.SM+('verify','sorting_s4_network_partition')\n    records += [audit(n,i,network) for n,i in functions(read(BASE+'slice/sort/shared/smallsort/verify/sorting_s4_network_partition.rs')).items()]\n"+anchor)
        path.write_text(data)
    path=HERE/'s4p2_contract_stacks.py';data=path.read_text().replace("keys = sorted(ACTIVE | {'kani_smallsort_s3_leaf','kani_smallsort_s4_partition'})", "flags = shlex.split(request['flags']['RUSTFLAGS'])\n    c.need(all(x.startswith('--cfg=') for x in flags), 'unsupported S4P2 cfg flags')\n    keys = sorted({'kani'} | {x[6:] for x in flags})")
    path.write_text(data)
    # Old exact fixtures are read by their old suites under a separate request context.
    (HERE/'fixtures/s4p-request.json').write_bytes((OLD/'CI-REQUEST.json').read_bytes())
    (HERE/'fixtures/s4p-workflow.yml').write_bytes((OLD.parent/'.github/workflows/ch8-s2.yml').read_bytes())
    put(OUT/'AUTHORITY.json',{'task':TASK,'notification_typo':'bf3ab9cff338f42010b28cf470ed393dfc690b73','correction':'Root correction in this thread; exact issuing commit verified locally','plan':'7253272c427eb9b564c79350ef73b231fa124298','review':'e287943e116a102d5950295b2629d80a62d1f922','profile':'SolHigh/FastOFF','native_CI_push_ledger_subagents_modelchanges':False})
    (OUT/'CURRENT-TASK.md').write_text('# W13 S4P2 offline implementation\n\nRuntime: Codex. Task '+TASK+'. SolHigh/FastOFF preserved.\nOwn new packet and isolated source/control siblings only. No native/CI/push/ledger/summary/modelchanges/subagents.\nTargeted tests before actual final committed-control Validate ONCE; exact package W14 review then root GO remain separate.\n')
    put(OUT/'CHECKPOINT.json',{'status':'IMPLEMENTING_OFFLINE','task':TASK,'source_parent':'97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a','control_parent':'9e14e033f9ee31522b571c127609dcdff76d230b','proof_credit':'NONE','native_status':'NOT_RUN','next':'Bind exact inventory/gates and targeted tests, commit siblings, final Validate once, seal packet'})
    print('S4P2 source and isolated control modules constructed')

if __name__=="__main__":main()
