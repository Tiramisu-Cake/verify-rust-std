# TIDYDOCS — PASS
Library `6443b4d99da9ff7d9bf33dee92bb035dbe66e838`, tree `6062452294ae749722ab3734993d9ef1af830dde`.
G1 `479cf06d-7189-4bba-bd72-285bbd1e329d`, source `0c472366d38e807a70561cc378c28601f237c007` (exact-packet GO).
Request `tidydocs-g1-20261106-01`, SHA256 `b35b328679111b715eeb0195c3686ff384cef8ea3e92c647dacce6157cc7bbce`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Cloud SUCCESS, COMPLETE, gate=true, Kani exit1 (ожидаемый контроль); diagnostic, standard4, jobs1, controls=true, inventory=false, 5 мин/корень; source/request/pool/tooling PASS.
Статика PASS: некомментарийные строки smallsort.rs побайтно равны v8c; verify token-identical кроме 20 message literals и точного нового контроля. Source-имена ordinary 233, cfg-on 268=233+12+22+1.
Cover-структура всех 233 ordinary сохранена; 966 runtime covers v8c повторно не измерялись. В verify нет строк >100, в smallsort.rs нет новых >100; запрещённая лексика отсутствует.

| Корень realcontracts:: | Status | с | Failed/total | Covers |
| --- | --- | ---: | ---: | ---: |
| rejects_swap_comparator_writing_outside_frame_u8 | FAILED | 1.8466973 | 1/205 | — |
| swap_safety_u8_backing9 | SUCCESS | 17.311901 | 0/219 | 6/6 |
| unstable_network_safety_u8_n9_stubbed | SUCCESS | 7.0849905 | 0/387 | 1/1 |
| sort4_safety_u64 | SUCCESS | 32.77827 | 0/293 | 3/3 |

Единственный упавший check: `Check that *var_9 is assignable` @ `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/realcontracts.rs:360` — `comparisons = comparisons.wrapping_add(1);`.
Состав failed checks полный: 1/205, только write set на счётчике; других failures нет. Положительные строки: 0/899 failed, covers 10/10, Σ57.1751615 с; все четыре Σ59.0218588 с. 28 unreachable positive checks — не covers.

| Файл от smallsort/ | Комментарии до→после | Файл от smallsort/ | Комментарии до→после |
| --- | ---: | --- | ---: |
| `../smallsort.rs` | 237→246 | `verify.rs` | 68→60 |
| `verify/allocationcontracts.rs` | 33→20 | `verify/assembly.rs` | 17→18 |
| `verify/comparators.rs` | 7→7 | `verify/merge.rs` | 58→56 |
| `verify/merge/specfix.rs` | 61→55 | `verify/mutations.rs` | 2→2 |
| `verify/network.rs` | 78→80 | `verify/permtags.rs` | 32→22 |
| `verify/realcontracts.rs` | 50→41 | `verify/scratchgeom.rs` | 13→12 |
| `verify/smoke.rs` | 3→3 | `verify/tailcontracts.rs` | 13→7 |
| `verify/types.rs` | 7→9 | `verify/wrap.rs` | 39→39 |

Примеры «было → стало»:

- network: «swap_if_less and insert_tail have no generic contract» → ordered profiles guard a canonical comparator; реальные frame proofs перечислены в карте.
- realcontracts: «G2 isolates exact lengths … timed out in G1» → «Constant lengths avoid a symbolic loop bound in the insertion proof».
- network: «every nonempty interior region» → «Fix the region’s start at index 1 to check both an untouched prefix and a suffix».

Не установлены минимальность unwind и отдельное преимущество Cadical/Kissat; атрибуты сохранены. Проверены только четыре строки G1; полного повторного proof/inventory нет, общие ограничения uninit/validity/immutable-byte/unwinding сохранены.
Cfg-on compiler: 2–64 с, первый CBMC 68 с; verify wall 2:13.56, max RSS 1706152 KiB. Расход $0.1350/$1.50, reserve0; builds1/2, repairs0, retries0; G2 не требуется.
Evidence: [summary](tidydocs/evidence/summary.md), [report](tidydocs/evidence/verification-report.json), [ledger](tidydocs/RUN-LEDGER.json), [статика](tidydocs/check-report.json).
