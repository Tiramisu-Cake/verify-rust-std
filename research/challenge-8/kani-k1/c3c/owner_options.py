"""Describe retained proof domains for observed/forecast risks; never edit proof code."""
import json
from pathlib import Path
import re

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
PREFIX='slice::sort::shared::smallsort::verify::'


def domain(name):
    module,leaf=name.removeprefix(PREFIX).split('::',1)
    n=re.search(r'_n(\d+)(?:$|_)',leaf)
    first_n=int(n.group(1)) if n else None
    nr=re.search(r'_n(\d+)_to(\d+)',leaf)
    ns=re.search(r'_n(\d+(?:_\d+)+)',leaf)
    n=(nr.group(1)+'..'+nr.group(2)) if nr else ns.group(1).replace('_',',') if ns else str(first_n) if first_n is not None else None
    typ='u64' if '_u64_' in leaf else 'u8' if '_u8_' in leaf else 'тип/размеры из source_entry'
    if module=='merge' and leaf.startswith('merge_contract_'):
        return (f'Полноширинный [{typ}; {n}], отдельный MaybeUninit destination той же длины; requires, включая sorted halves; lt_{typ} сравнивает ключ value>>1.',
                f'Контракт bidirectional_merge для этого T/N. Проверки general/stable с stub_verified(bidirectional_merge) требуют соответствующего базового домена; при u64 N16 это обе ordinary route proofs. Existing allocation-locality transfer gaps остаются.')
    if module=='network' and leaf.startswith('insertion_permutation_'):
        offset=13 if n and first_n>=13 else 9
        return (f'Любой полноширинный [{typ}; {n}], произвольный probe и все read-only nondeterministic comparison sequences; реальная insertion_sort_shift_left с offset={offset}, без sorted-prefix assume; probe multiplicity preserved.',
                f'Отдельная insertion permutation obligation для N{n}; поддерживает только соответствующее структурное рассуждение о permutation network+suffix, не общий машинно-проверенный full-route theorem.')
    if module=='network' and leaf.startswith('network_correctness_'):
        prop='sortedness и произвольный probe multiset' if n and first_n<9 else 'sortedness; permutation N>=9 здесь не является прямым full-route assert'
        return (f'Любой полноширинный [{typ}; {n}], настоящий unstable trait entry и strict_less; {prop}.',
                ('При N>=9 source описывает композицию со структурной перестановкой сети и отдельно проверенной реальной перестановкой insertion-tail; этот harness сам утверждает только sortedness. '
                 'При N<9 этот harness сам проверяет probe multiplicity. В обоих случаях соседний N и safety-only route witness не заменяют domain.'))
    if module=='network' and leaf.startswith('insert_tail_contract_'):
        st=re.search(r'_start(\d+)',leaf);tail=re.search(r'_tail(\d+)',leaf)
        region=f"START={st.group(1) if st else '?'}, tail={tail.group(1) if tail else 'START+1..16'}"
        return (f'Полноширинный [u64;17], {region}, lt_u64, requires sorted prefix и frame до begin/после tail; unwind25.',
                'Теряется ровно указанный shifted-region contract domain. Иные begin/allocation instances не подменяют его; общий allocation-locality transfer не заявляется доказанным.')
    if module=='correct' and ('general_' in leaf or 'stable_' in leaf):
        route='stable Freeze' if '_stable_' in leaf and '_general_stable_' not in leaf else 'direct general' if '_general_stable_' not in leaf else 'оба bool-маршрута'
        return (f'Полноширинный [{typ};{n}], {route}, scratch48 где требуется; sortedness и произвольный probe count; sort4 real, insertion/merge verified stubs.',
                'Теряется соответствующее верхнее композиционное correctness утверждение; primitive contract proofs не заменяют этот caller proof.')
    if module=='correct' and leaf.startswith('sorted_permutation_fallback_'):
        return (f'Полноширинный [{typ};{n}], fallback route; asserts sortedness и probe multiplicity для произвольного входа и comparator с key value>>1.',
                'Harness применяет stub_verified(insert_tail): композиция зависит от соответствующего insertion-tail контракта и порядка ключа comparator. Не доказывает general/stable route или другие T/N.')
    if module=='merge' and leaf.startswith('route_safety_'):
        route=('direct general u64' if 'general_u64_' in leaf else
               'non-Copy general u64' if 'noncopy_u64_' in leaf else
               'stable u64' if 'stable_u64_' in leaf else 'choice among direct general, non-Copy general, and stable routes')
        return (f'Safety/reachability only for [{typ};{n}], {route}; exercises real upper-route callee and requires normal-return cover (unwind 34).',
                'This witness does not assert sortedness, permutation, or route equivalence. It has no direct correctness-proof dependency; removing it loses only this route/length safety witness, not the corresponding correctness assertion.')
    if module=='merge' and 'sorted_permutation_' in leaf:
        return (f'Полноширинный [{typ};{n}], указанный general/stable/fallback маршрут; sortedness и probe-count assertions. Точный scratch/stub scope виден в source_entry и macro helper.',
                'Теряется этот upper-route correctness instance. Для general/stable bidirectional_merge stub остаётся предпосылкой композиции; не переносить утверждение на другие T/N/allocation.')
    if module=='types':
        return (f'LogicalByte trait-entry correctness из source_entry: Cell<u8> (!Freeze) либо DropKey (Freeze non-Copy), длины {n or "0..2 / из invocation"}; stable/unstable branches и logical sortedness/multiset.',
                'Теряется соответствующий non-Freeze/non-Copy trait-entry domain. Copy u8/u64 proofs и другие длины его не заменяют.')
    return ('Точный инстанс (тип, длины, offsets, маршруты) сохранён в source_entry; свойства определяет указанный macro/helper. Никакое сужение или удаление не применено.',
            'Удаление утратит именно этот именованный proof/witness domain; зависимость дополнительных композиционных утверждений требует source review, она не выдумывается по одному имени.')


def source_entry(name):
    module,leaf=name.removeprefix(PREFIX).split('::',1)
    path=ROOT/'library/core/src/slice/sort/shared/smallsort/verify'/f'{module}.rs'
    if not path.exists():return '',None,''
    text=path.read_text();m=re.search(r'\b'+re.escape(leaf)+r'\b',text)
    if not m:return str(path.relative_to(ROOT)),None,''
    line=text.count('\n',0,m.start())+1
    ls=text.splitlines();start=max(0,line-3);end=min(len(ls),line+6)
    snippet=' '.join(x.strip() for x in ls[start:end])
    return str(path.relative_to(ROOT)),line,snippet[:1800]


def main():
    data=json.loads((BASE/'measurements.json').read_text())
    records=[]
    for row in data.get('ordinary_risk_register',[]):
        relevant=(row['status']!='SUCCESS' or any(flag in row.get('flags',[]) for flag in ('MAC_POINT_OVER_300','MAC_OBSERVED_TAIL_OVER_300','MAC_CENSORED_LOWER_TRANSFER_OVER_300','HISTORICAL_MAC_TIMEOUT600_NOT_RETESTED')))
        if not relevant:continue
        text,deps=domain(row['name']);file,line,entry=source_entry(row['name'])
        records.append(dict(name=row['name'],status=row['status'],gcb_time_s=row['gcb_time_s'],mac_point_forecast_s=row['mac_point_forecast_s'],mac_stress_scenario_s=row['mac_observed_tail_transfer_s'],mac_censored_lower_transfer_s=row.get('mac_censored_lower_transfer_s'),flags=','.join(row['flags']),domain_if_omitted=text,dependent_claims=deps,source_file=file,source_line=line,source_entry=entry,action='НЕ ПРИМЕНЕНО: proof остаётся ordinary; опции владельцу — новый П-6, продолжение разбиений с union/cost audit или явное принятие раскрытой потери домена.'))
    keys=['name','status','gcb_time_s','mac_point_forecast_s','mac_stress_scenario_s','mac_censored_lower_transfer_s','flags','domain_if_omitted','dependent_claims','source_file','source_line','source_entry','action']
    with (BASE/'owner-risk-options.tsv').open('w') as f:
        f.write('\t'.join(keys)+'\n')
        for r in records:f.write('\t'.join(str(r[k]).replace('\t',' ').replace('\n',' ') for k in keys)+'\n')
    (BASE/'owner-risk-options.json').write_text(json.dumps(dict(applied=False,scope='C3c observed non-success / transferred scenario over300; not a recommendation to delete ordinary proofs',rows=records),indent=2)+'\n')
    print('owner options:',len(records),'retained ordinary domains; no proof edits')

if __name__=='__main__':main()
