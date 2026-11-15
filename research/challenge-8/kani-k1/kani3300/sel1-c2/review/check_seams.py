#!/usr/bin/env python3
"""Rust extraction seam audit using source tokens only, never a compiler.

Inventories EVERY declaration/impl/use in changed .rs files; rejects generic self types
without explicit arguments in impl headers, unexpected signature/import changes against
both baseline and frozen reference, and mismatched arity at explicitly bound API sites.
All same-spelling consumers are listed separately for human binding review. This is a
bounded static dependency check, not Rust name resolution, typechecking or proof.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

TOKEN = re.compile(r"'[A-Za-z_]\w*|[A-Za-z_]\w*|\d+|::|->|=>|\.\.|[^\s]")


def mask(text):
    """Preserve offsets while removing comments and string/char literals."""
    out = list(text)
    i = 0
    while i < len(text):
        start = i
        if text.startswith('//', i):
            end = text.find('\n', i)
            i = len(text) if end < 0 else end
        elif text.startswith('/*', i):
            i += 2
            depth = 1
            while depth and i < len(text):
                if text.startswith('/*', i):
                    depth += 1; i += 2
                elif text.startswith('*/', i):
                    depth -= 1; i += 2
                else:
                    i += 1
            if depth:
                raise ValueError('unclosed block comment')
        else:
            raw = re.match(r'(?:br|cr|r)(#*)"', text[i:])
            char = re.match(r"(?:b)?'(?:\\(?:u\{[^}]*\}|x..|.)|[^'\\\n])'", text[i:])
            if raw:
                end = text.find('"' + raw[1], i + len(raw[0]))
                if end < 0: raise ValueError('unclosed raw literal')
                i = end + 1 + len(raw[1])
            elif char:
                i += len(char[0])
            elif text[i] == '"':
                i += 1
                while i < len(text) and text[i] != '"':
                    i += 2 if text[i] == '\\' else 1
                if i >= len(text): raise ValueError('unclosed string')
                i += 1
            else:
                i += 1
                continue
        for k in range(start, i):
            if text[k] != '\n': out[k] = ' '
    return ''.join(out)


def tokens(text):
    return [(m.group(), m.start()) for m in TOKEN.finditer(mask(text))]


def balanced(ts):
    stack, pairs = [], {}
    for i, (v, _) in enumerate(ts):
        if v in ('(', '[', '{'): stack.append((v, i))
        elif v in (')', ']', '}'):
            if not stack or stack[-1][0] != {')':'(', ']':'[', '}':'{'}[v]:
                raise ValueError('unbalanced delimiter')
            _, k = stack.pop(); pairs[k] = i
    if stack: raise ValueError('unclosed delimiter')
    return pairs


def header_end(ts, i, pairs):
    while i < len(ts):
        if ts[i][0] in ('{', ';'): return i
        if ts[i][0] in ('(', '['): i = pairs[i]
        i += 1
    raise ValueError('unterminated header')


def inventory(text):
    ts = tokens(text); pairs = balanced(ts); rows = []; scopes = []
    for i, (v, pos) in enumerate(ts):
        if v not in ('fn', 'struct', 'enum', 'trait', 'impl', 'use', 'mod', 'type'): continue
        # impl Trait in a return type is not an impl block.
        if v == 'impl' and i and ts[i-1][0] not in ('}', ';', '{', ']', 'unsafe'):
            continue
        if v == 'fn' and ts[i+1][0] == '(': continue  # bare fn type
        end = next(k for k in range(i+1,len(ts)) if ts[k][0]==';') if v=='use' else header_end(ts, i+1, pairs)
        sig = ' '.join(t[0] for t in ts[i:end])
        if v in ('impl', 'use'):
            name = sig
        else:
            name = ts[i+1][0]
        parents = [s['scope'] for s in scopes if s['start'] < i < s['end']]
        # Function bodies contain local type aliases/closures; keep a stable path.
        row = {'kind':v, 'name':name, 'container':parents, 'line':text.count('\n',0,pos)+1,
               'signature':sig, 'token_start':i, 'token_end':end}
        rows.append(row)
        if v in ('impl','mod') and ts[end][0] == '{':
            scopes.append({'scope':sig, 'start':end, 'end':pairs[end]})
    return rows, ts, pairs


def import_leaves(signature):
    vals=signature.split()[1:]
    def parse(items,prefix=()):
        result=[]; part=[]; depth=0; chunks=[]
        for v in items+[',']:
            if v==',' and depth==0:
                if part: chunks.append(part)
                part=[]; continue
            if v=='{': depth+=1
            elif v=='}': depth-=1
            part.append(v)
        for chunk in chunks:
            if '{' in chunk:
                opening=chunk.index('{')
                base=prefix+tuple(v for v in chunk[:opening] if v!='::')
                result.extend(parse(chunk[opening+1:-1],base))
            else:
                result.append(prefix+tuple(v for v in chunk if v!='::'))
        return result
    return set(parse(vals))


def norm_key(row):
    # Ignore generic substitutions in impl containers to pair old/new declarations.
    def strip(s): return re.sub(r'<[^<>]*>', '', s).strip()
    return (row['kind'], tuple(strip(s) for s in row['container']),
            strip(row['name']) if row['kind']=='impl' else row['name'])


def angle_arguments(values, opening):
    depth=0; args=[]; current=[]
    for i in range(opening+1,len(values)):
        v=values[i]
        if v=='>' and depth==0:
            if current:args.append(current)
            return args
        if v==',' and depth==0:
            if current:args.append(current)
            current=[];continue
        if v=='<':depth+=1
        elif v=='>':depth-=1
        current.append(v)
    raise ValueError('unterminated generic argument list')


def generic_declarations(rows,ts):
    result={}
    for r in rows:
        if r['kind'] in ('struct','enum'):
            h=[v for v,_ in ts[r['token_start']:r['token_end']]]
            if len(h)>2 and h[2]=='<':
                params=angle_arguments(h,2)
                result[r['name']]=(sum('=' not in p for p in params),len(params))
    return result


def generic_impl_errors(rows, ts, path, catalog=None):
    types=dict(catalog or {});types.update(generic_declarations(rows,ts));errors=[]
    for r in rows:
        if r['kind'] != 'impl':continue
        h=[v for v,_ in ts[r['token_start']:r['token_end']]]
        for name,bounds in types.items():
            required,total=(bounds,bounds) if isinstance(bounds,int) else bounds
            for k,v in enumerate(h):
                if v!=name or not required:continue
                has_args=k+1<len(h) and h[k+1]=='<'
                actual=len(angle_arguments(h,k+1)) if has_args else 0
                if actual<required or actual>total:
                    errors.append({'path':path,'line':r['line'],'type':name,
                        'reason':'generic type in impl header lacks required explicit arguments',
                        'actual_arguments':actual,'required_arguments':required,'total_arguments':total,
                        'signature':r['signature']})
    return errors


def call_arity(ts, opening, pairs):
    """Count syntactic arguments, skipping nested delimiters and turbofish."""
    end = pairs[opening]; i = opening+1; count=0; has=False; angle=0
    while i<end:
        v=ts[i][0]
        if v in ('(', '[', '{'):
            has=True; i=pairs[i]+1; continue
        if v=='<' and i and (ts[i-1][0]=='::' or angle): angle+=1
        elif v=='>' and angle: angle-=1
        elif v==',' and not angle:
            if has: count+=1
            has=False; i+=1; continue
        else: has=True
        i+=1
    return count+int(has)


def audit(repo, base, head, reference, contracts):
    def git(*args): return subprocess.check_output(['git','-C',str(repo),*args]).decode()
    cache={}
    def source(ref,path):
        if (ref,path) not in cache:
            present=git('ls-tree',ref,'--',path).strip()
            cache[ref,path]=git('show',ref+':'+path) if present else ''
        return cache[ref,path]
    paths=[p for p in git('diff','--name-only',base,head).splitlines() if p.endswith('.rs')]
    files=[]; errors=[]; changed_names=set(); generic_catalog={}
    for path in paths:
        old,_,_=inventory(source(base,path)); current,ts,_=inventory(source(head,path)); final,_,_=inventory(source(reference,path))
        old_sigs={r['signature'] for r in old}; final_sigs={r['signature'] for r in final}
        allowed_imports=set().union(*(import_leaves(r['signature']) for r in old+final if r['kind']=='use'))
        generic_catalog.update(generic_declarations(current,ts))
        changed=[]
        for r in current:
            if r['signature'] not in old_sigs:
                r=dict(r); r['reference_match']=r['signature'] in final_sigs
                r['baseline_F_import_union_match'] = r['kind']=='use' and import_leaves(r['signature']) <= allowed_imports
                if not r['reference_match'] and not r['baseline_F_import_union_match']:
                    errors.append({'path':path,'line':r['line'],'reason':'new signature/import is neither baseline nor F','signature':r['signature']})
                changed.append(r)
                if r['kind']=='fn': changed_names.add(r['name'])
        removed=[r for r in old if r['signature'] not in {c['signature'] for c in current}]
        errors.extend(generic_impl_errors(current,ts,path))
        files.append({'path':path, 'head_sha256':hashlib.sha256(source(head,path).encode()).hexdigest(),
                      'declarations_impls_uses_total':len(current),'changed_or_added':changed,'removed_or_replaced':removed,
                      'imports_current':[r for r in current if r['kind']=='use'],
                      'impls_current':[r for r in current if r['kind']=='impl']})
    # All compiler source files, including unchanged consumers and similarly named helpers.
    all_paths=[p for p in git('ls-tree','-r','--name-only',head,'--','kani-compiler').splitlines() if p.endswith('.rs')]
    references={name:[] for name in sorted(changed_names)}; bound=[]
    for path in all_paths:
        text=source(head,path); rows,ts,pairs=inventory(text)
        errors.extend(generic_impl_errors(rows,ts,path,generic_catalog))
        for i,(v,pos) in enumerate(ts):
            if v in references:
                references[v].append({'path':path,'line':text.count('\n',0,pos)+1,
                                      'context':' '.join(t[0] for t in ts[max(0,i-3):i+5])})
        for c in contracts:
            if not re.fullmatch(c['path_regex'],path): continue
            wanted=c['tokens']
            for i in range(len(ts)-len(wanted)):
                if [v for v,_ in ts[i:i+len(wanted)]]!=wanted: continue
                opening=i+len(wanted)
                if ts[opening][0]!='(': continue
                if i and ts[i-1][0]=='fn': continue
                actual=call_arity(ts,opening,pairs)
                row={'contract':c['id'],'path':path,'line':text.count('\n',0,ts[i][1])+1,
                     'arity':actual,'expected':c['arity']}
                bound.append(row)
                if actual!=c['arity']: errors.append({**row,'reason':'bound call arity mismatch'})
    for c in contracts:
        count=sum(r['contract']==c['id'] for r in bound)
        if count!=c['count']:
            errors.append({'contract':c['id'],'actual_count':count,'expected_count':c['count'],'reason':'bound callsite coverage mismatch'})
    errors=list({json.dumps(e,sort_keys=True):e for e in errors}.values())
    return {'status':'PASS_BOUNDED_STATIC_SEAM_AUDIT' if not errors else 'FAIL',
            'base':base,'head':head,'reference':reference,'changed_rust_file_count':len(paths),
            'generic_types_checked_repo_wide':sorted(generic_catalog),'files':files,'bound_api_calls':bound,'all_same_spelling_references':references,'errors':errors,
            'limits':'Source-token inventory, local generic impl checks and explicitly bound call arities; no Rust name resolution/typecheck, macro expansion, trait resolution or native build. Whole-file signature/import inventory and lexical references require human review.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['repo','base','head','reference','contracts','out']:p.add_argument('--'+name,required=True)
    a=p.parse_args(); contracts=json.loads(Path(a.contracts).read_text())
    result=audit(a.repo,a.base,a.head,a.reference,contracts)
    result['tool_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['contracts_sha256']=hashlib.sha256(Path(a.contracts).read_bytes()).hexdigest()
    result['native_build']='NOT_RUN'
    Path(a.out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','base','head','changed_rust_file_count','errors']}))
    raise SystemExit(bool(result['errors']))

if __name__=='__main__':main()
