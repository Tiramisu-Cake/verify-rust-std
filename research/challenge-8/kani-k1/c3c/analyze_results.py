"""C3c evidence analysis: only bounded exports, source-bound requests and supplied historical TSVs."""
import collections
from datetime import datetime
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import statistics
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
EVIDENCE=BASE/'evidence'
PREFIX='slice::sort::shared::smallsort::verify::'
SESSION=json.loads((BASE/'session.json').read_text())
spec=importlib.util.spec_from_file_location('lane',ROOT/'research/challenge-8/kani-k1/tools/kani_k1.py')
lane=importlib.util.module_from_spec(spec);spec.loader.exec_module(lane)

def metadata(lines):
    return dict(line.split('=',1) for line in lines if '=' in line and '\t' not in line
                and re.fullmatch('[a-z_0-9]+',line.split('=',1)[0]))

def read_build(entry):
    label=entry['label'];sha=entry['sha']
    rb=subprocess.check_output(['git','show',sha+':research/challenge-8/kani-k1/RUN-REQUEST.json'],cwd=ROOT)
    req=json.loads(rb)
    identity=dict(head_sha=sha,build_id=entry['build_id'],request_id=req['request_id'],request_sha256=hashlib.sha256(rb).hexdigest())
    rows=[];offset=0;total=None
    for file in sorted(EVIDENCE.glob(label+'.*.rows.tsv')):
        lines=file.read_text().splitlines();split=lines.index('name\tstatus\ttime_s\tchecks\tcovers');meta=metadata(lines[:split])
        for k,v in identity.items():assert meta[k]==v,(file,k)
        assert int(meta['offset'])==offset
        data=lines[split+1:];assert len(data)==int(meta['count'])
        for line in data:
            name,status,seconds,checks,covers=line.split('\t')
            secs=None if seconds in ('','None') else float(seconds)
            assert secs is None or (math.isfinite(secs) and secs>=0)
            rows.append(dict(name=name,status=status,time_s=secs,checks=checks,covers=covers))
        offset+=len(data);total=int(meta['total'])
        assert meta['next_offset']==('done' if offset==total else str(offset))
    assert total is not None and offset==total,(label,offset,total)
    inventory=[];offset=0;invtotal=None;invhash=None
    for file in sorted(EVIDENCE.glob(label+'.*.inventory.page')):
        lines=file.read_text().splitlines();meta=metadata(lines)
        for k,v in identity.items():assert meta[k]==v,(file,k)
        names=[line for line in lines if line.startswith(PREFIX)]
        assert int(meta['offset'])==offset and len(names)==int(meta['count'])
        inventory+=names;offset+=len(names);invtotal=int(meta['total']);invhash=meta['names_sha256']
        assert meta['next_offset']==('done' if offset==invtotal else str(offset))
    if req.get('inventory') and not entry.get('setup_failed'):
        assert invtotal==len(inventory) and len(inventory)==len(set(inventory))
        assert hashlib.sha256(('\n'.join(inventory)+'\n').encode()).hexdigest()==invhash
    md=(EVIDENCE/(label+'.summary.md')).read_text()
    assert sha in md and identity['request_sha256'] in md
    status=re.search(r'^# K-1 run `[^`]+`: (\w+)',md,re.M).group(1)
    gate=re.search(r'- gate: (\w+);',md).group(1)
    wall=re.search(r'- whole run, including compilation: max RSS (\S+) KiB, wall (.*?) \(',md)
    peakpath=EVIDENCE/(label+'.peaks.txt')
    peaks=lane.parse_peaks(peakpath.read_text() if peakpath.exists() else None)
    memory=[]
    for file in sorted(EVIDENCE.glob(label+'.process-*.txt')):
        for line in file.read_text().splitlines():
            if line.startswith('{'):memory.append(json.loads(line))
    build_metadata=json.loads((EVIDENCE/(label+'.status.json')).read_text())
    assert build_metadata['id']==entry['build_id'] and build_metadata['source_sha']==sha
    if build_metadata.get('startTime') and build_metadata.get('finishTime'):
        ts=lambda s:datetime.fromisoformat(s.replace('Z','+00:00'))
        build_metadata['wall_seconds']=(ts(build_metadata['finishTime'])-ts(build_metadata['startTime'])).total_seconds()
        build_metadata['ledger_cost_usd']=math.ceil(build_metadata['wall_seconds']/60)*.0135
    for row in rows:
        row.update(source_sha=sha,build_id=entry['build_id'],request_id=req['request_id'])
    if 'memory' in label:
        for record in memory:
            assert record.get('head_sha')==sha and record.get('build_id')==entry['build_id'],(label,'process provenance')
    ours=[r for r in rows if r['name'].startswith(PREFIX)]
    def metrics(rs):
        timed=[r['time_s'] for r in rs if r['time_s'] is not None]
        return dict(count=len(rs),statuses=dict(collections.Counter(r['status'] for r in rs)),timed_count=len(timed),sum_observed_verification_s=round(sum(timed),6),max_observed_s=max(timed,default=None),censored_or_untimed=sum(r['time_s'] is None for r in rs))
    return dict(label=label,**identity,build_metadata=build_metadata,request=req,summary_status=status,gate=gate,rows=rows,ordinary_inventory=inventory,all=metrics(rows),smallsort=metrics(ours),smallsort_share_of_observed_verification_time=(sum(r['time_s'] or 0 for r in ours)/sum(r['time_s'] or 0 for r in rows) if any(r['time_s'] for r in rows) else None),command_wall=wall.group(2) if wall else None,gnu_time_max_child_rss_kb=wall.group(1) if wall else None,peaks=peaks,process_memory=memory)

def main():
    builds={}
    for entry in SESSION['builds']:
        if (EVIDENCE/(entry['label']+'.summary.md')).exists():
            builds[entry['label']]=read_build(entry)
    baseline=builds.get('baseline-memory') or builds.get('baseline');candidate=builds.get('candidate');full=builds.get('autoharness')
    memory_parts=[builds.get('candidate-memory-1'),builds.get('candidate-memory-2')]
    if all(memory_parts):
        combined=[row for part in memory_parts for row in part['rows']]
        assert len(combined)==54 and len({r['name'] for r in combined})==54
        candidate=dict(rows=combined,summary_status='COMPLETE' if all(part['summary_status']=='COMPLETE' for part in memory_parts) else 'PARTIAL',source_builds=[part['build_id'] for part in memory_parts],request=dict(harness_timeout_minutes=5),process_memory=[record for part in memory_parts for record in part['process_memory']])
    macrows=[line.split('\t') for line in (BASE.parent/'c3c-inputs/mac-times.tsv').read_text().splitlines()]
    mac={name:float(sec) for name,sec,status in macrows if name.startswith(PREFIX)}
    historical_timeouts=set(PREFIX+n for n in ('merge::merge_contract_u64_n16','network::insertion_permutation_u64_n12','network::insert_tail_contract_u64_start1'))
    calibration=[];families=collections.defaultdict(list)
    if baseline:
        for row in baseline['rows']:
            name=row['name'];family=name[len(PREFIX):].split('::')[0]
            c=dict(name=name,family=family,gcb_status=row['status'],gcb_time_s=row['time_s'],mac_time_s=mac.get(name),mac_censored_timeout_s=600 if name in historical_timeouts else None,point_ratio=None,ratio_lower_bound=None,ratio_upper_bound=None)
            if baseline['summary_status'] != 'COMPLETE':
                c['not_eligible_reason']='Baseline run is not COMPLETE/consistent; preserve rows without point calibration'
            elif name in mac and row['status']=='SUCCESS' and row['time_s']:
                c['point_ratio']=mac[name]/row['time_s']
            elif name in mac and row['status']=='TIMEOUT':
                c['ratio_upper_bound']=mac[name]/(60*baseline['request']['harness_timeout_minutes'])
            elif name in historical_timeouts and row['status']=='SUCCESS' and row['time_s']:
                c['ratio_lower_bound']=600/row['time_s']
            c['model_binding']='P6 6cfc76cb to baseline e965: common callee/stubs/solver/unwind source unchanged; baseline library tree checked at dispatch'
            calibration.append(c);families[family].append(c)
    family_stats={}
    for family,rs in families.items():
        points=sorted(r['point_ratio'] for r in rs if r['point_ratio'] is not None)
        lows=[r['ratio_lower_bound'] for r in rs if r['ratio_lower_bound'] is not None]
        family_stats[family]=dict(n_point=len(points),n_censored=sum(r['gcb_status']=='TIMEOUT' or r['mac_censored_timeout_s'] is not None for r in rs),n_unusable_or_unmeasured=sum(r['point_ratio'] is None and r['gcb_status']!='TIMEOUT' and r['mac_censored_timeout_s'] is None for r in rs),median=statistics.median(points) if points else None,min=min(points,default=None),max_observed=max(points,default=None),p90_observed=points[max(0,math.ceil(.9*len(points))-1)] if points else None,censored_lower_bounds=lows,censored_upper_bounds=[r['ratio_upper_bound'] for r in rs if r['ratio_upper_bound'] is not None],stress_transfer_coefficient=max(points+lows,default=None),coefficient_is_upper_bound=False)
    paired=[]
    if baseline and candidate:
        old={r['name']:r for r in baseline['rows']};new={r['name']:r for r in candidate['rows']}
        domainmap=json.loads((BASE/'paired-domain-map.json').read_text());mapping=dict(domainmap['old_domains'])
        if all(memory_parts):mapping.update(domainmap.get('additional_memory_calibration_domains',{}))
        for name,successors in mapping.items():
            rs=[new.get(n,dict(name=n,status='MISSING',time_s=None)) for n in successors]
            allok=all(r['status']=='SUCCESS' and r['time_s'] is not None for r in rs)
            paired.append(dict(old_name=name,baseline=old.get(name),successors=rs,candidate_sum_observed_s=sum(r['time_s'] or 0 for r in rs),candidate_sum_complete=allok,candidate_max_observed_s=max((r['time_s'] for r in rs if r['time_s'] is not None),default=None),note='Sum of Verification Time, not CPU or wall; censored members are not replaced by cutoff'))
    registry=[]
    if full:
        inventory=full['ordinary_inventory'];lookup=collections.defaultdict(list)
        for row in full['rows']:lookup[row['name']].append(row)
        expected=set((BASE/'predicted-ordinary.txt').read_text().splitlines())
        full['inventory_prediction_missing']=sorted(expected-set(inventory));full['inventory_prediction_extra']=sorted(set(inventory)-expected)
        full['inventory_results_missing']=[n for n in inventory if not lookup[n]]
        full['inventory_results_duplicated']=[n for n in inventory if len(lookup[n])>1]
        for name in inventory:
            row=lookup[name][0] if len(lookup[name])==1 else dict(status='MISSING_OR_DUPLICATE',time_s=None,covers='',checks='')
            family=name[len(PREFIX):].split('::')[0];fs=family_stats.get(family,{})
            secs=row['time_s'];median=fs.get('median');stress=fs.get('stress_transfer_coefficient')
            point=secs*median if secs is not None and median is not None else None
            tail=secs*stress if secs is not None and stress is not None else None
            flags=[]
            if full['summary_status']!='COMPLETE':flags.append('RUN_'+full['summary_status'])
            if row['status']!='SUCCESS':flags.append(row['status'])
            if point is None:flags.append('NO_MAC_POINT_FORECAST')
            if point is not None and point>300:flags.append('MAC_POINT_OVER_300')
            if tail is not None and tail>300:flags.append('MAC_OBSERVED_TAIL_OVER_300')
            memory=[r for r in full['process_memory'] if r.get('harness')==name]
            registry.append(dict(name=name,family=family,status=row['status'],gcb_time_s=secs,mac_point_forecast_s=point,mac_observed_tail_transfer_s=tail,flags=flags,direct_cbmc_peak_kb=max((r['peak_kb'] for r in memory if r['cmd']=='cbmc'),default=None),forecast_is_acceptance=False,forecast_method='Within-family transfer of source-unchanged baseline ratios onto changed candidate models; assumption, not bound'))
    out=dict(schema='c3c-analysis-v1',builds=builds,calibration_rows=calibration,calibration_families=family_stats,paired_domains=paired,ordinary_risk_register=registry,limitations=['No complete baseline autoharness run: no measured full-job improvement or Ubuntu shutdown cause established.','Three Ubuntu in-flight names absent from supplied TSV.','Historical TSV times rounded to 0.1s; censored observations retained.','Family coefficient transfer onto changed models is forecast only; no guaranteed macOS bound.','RSS is not physical RAM; active-set attribution is ambiguous unless direct_harness is recorded.'])
    (BASE/'measurements.json').write_text(json.dumps(out,indent=2)+'\n')
    with (BASE/'calibration.tsv').open('w') as f:
        keys=['name','family','mac_time_s','gcb_status','gcb_time_s','point_ratio','ratio_lower_bound','ratio_upper_bound']
        f.write('\t'.join(keys)+'\n')
        for r in calibration:f.write('\t'.join(str(r.get(k,'')) for k in keys)+'\n')
    with (BASE/'risk-register.tsv').open('w') as f:
        keys=['name','family','status','gcb_time_s','mac_point_forecast_s','mac_observed_tail_transfer_s','flags']
        f.write('\t'.join(keys)+'\n')
        for r in registry:f.write('\t'.join(','.join(r[k]) if isinstance(r[k],list) else str(r[k]) for k in keys)+'\n')
    print(json.dumps(dict(builds={label:{k:b[k] for k in ('summary_status','gate','all','smallsort','command_wall')} for label,b in builds.items()},calibration_families=family_stats,registry_count=len(registry)),indent=2))

if __name__=='__main__':main()
