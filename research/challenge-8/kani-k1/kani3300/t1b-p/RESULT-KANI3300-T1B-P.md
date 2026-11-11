# KANI3300 T1b-P — RESULT
Build `1c007e31-5bb6-459d-8197-9354ce20a66c`: Cloud SUCCESS; Kani build279s; verify COMPLETE/exit0/gate=true; один dispatch, повторов0.
Source `4301de66b941a380dfe9a54d16a5a10378fe55d1`; request SHA256 `d81b1b389cb37ab3d6ba1ef8e27f6dee1edda57a433af6096b68cee46c5fb3b1` MATCH.
Proto `94467a24484f1d57315ebbcde7f024dd27576a00`; pin f046b70644e113be0df9c22c2e6ea44a65a57566; applied tree b8575e61d76709951f461b3eda70726be43d3636 MATCH.
Patch SHA256 20075382fe1e7fa63a31c25adfe4b9c722ce42a86dab0bd105f96d571acdea6a; library919cc3e2, tooling, argv/env, controls/uninit,1m/jobs1 MATCH; ровно C2 trio/один invocation.

| Root suffix uninit_probe:: | C2 → P | Failed/total C2 → P | Covers C2 = P |
|---|---|---|---|
| cmp3_into_iter_next | SUCCESS → SUCCESS | 0/254 → 0/254 | 3/3 |
| cmp3_index_range_len | FAILED → SUCCESS | 2/28 → 0/20 | 1/1 |
| cmp3_manually_drop_unsized_len | SUCCESS → SUCCESS | 0/92 → 0/84 | 2/2 |

Actual codegen order next→manual→index: seq37/78/121, invocation8614:0/unit0; C2 тот же порядок37/77/133; не вывод из request enumeration.
next сохранил свои header CheckRef ((*_1).1/.0:usize), seq69/71 (C2:68/70); собственный DelayedUbPass writer73→GOTO consumer77.
Оба next hash9bae019701b64b9b/dump1685B/dump_ok=true, как C2 writer72→consumer76; инструментация не исчезла повсюду; next имеет12 unreachable checks.
Все len consumers имеют Instance core::ops::index_range::IndexRange::len и symbol `_RNvMNtNtCs6yCX8DdYmoX_4core3ops11index_rangeNtB2_10IndexRange3lenB6_`, phase=before_goto_blocks.
manual: собственный miss_creator84→local len snapshot85 hash8e83681b4d5b4436→scan99(8 instr/0 ops)→consumed118, hash8e83681b4d5b4436/422B/dump_ok=true.
index: собственный miss_creator127→scans128/154(8 instr/0 ops)→consumed161, hash8e83681b4d5b4436/422B/dump_ok=true; отдельный local len snapshot не сохранён (UNKNOWN).
C2 manual/index consumed130/187: hash9bae019701b64b9b/1685B, matching last_writer=next; их scans111/180 видели18 instr/0 ops. В P оба consumed hash совпали с исходным len warmup23.
P manual/index last_writer всё ещё DelayedUbPass/next/codegen/unit0, writer hash9bae019701b64b9b ≠ actual consumed8e83681b4d5b4436: это не свидетельство переноса изменённого тела.
Строгий no-foreign-last_writer/provenance критерий UNKNOWN: unit-scoped диагностическая метка может быть stale; независимого разрешения provenance нет; PASS не присваивается.
Caller local-before→consumed: manual eb513feae7068629→2baa0ab19a2a9844 (P81/120), index9966dbeee7ac8b6f→37806c4e63230639 (P124/159); обе пары равны C2.
P caller writers83/126 — собственный root/codegen/local_pass_5; C2 writers35/29 были собственный root/warmup; caller body hashes сохранены.

| Критерий / ветвь интерпретации | Итог |
|---|---|
| Три SUCCESS + actual order + собственные next CheckRefs | PASS по наблюдаемым diagnostics |
| Прежнее чужое изменённое len body у manual/index | P потребляет исходный hash; поддержка causal isolation для этого false-positive |
| Полная witness/provenance приёмка | UNKNOWN; нельзя объявить весь ACCEPTANCE PASS |

Вывод: смена lifetime/cache isolation устранила данный index false-positive при сохранении next checks; это причинная поддержка shared-cache гипотезы, не полная production acceptance.
Trace PARTIAL/complete=false; seen=emitted161/omitted0; errors=[]; external_cache_witness_cap1777/external_witness_cap37. Девять bounded pages по returned next_start, не полная witness coverage.
Sidecar94251B SHA2564d93b9a954ed4c3a32e8e61058c617404e34dd3c3c1ae913fec410715557d586; TRACE-KEYS-P.json/EVIDENCE-INDEX-P.json сохраняют identities и receipts.
Brief HTTP404; bounded K1 summary/trace-field использованы с identity guards; archive/inventory integrity NOT_ESTABLISHED; raw logs/archives не читались.
Стоимость отдельного kani3300-t1b-pilot: $0.1485 (11 rounded pool min×$0.0135), cap$0.50, initial reserve$0.4455→terminal$0; unused$0.3515 retired/carry0; старый T1b carry$0.
Calibration positive/negative и native IntoIter/compound/padding NOT_RUN; runtime R-byte причинность UNKNOWN; noncryptographic MIR hashes не binding; независимый B1/B2/proof credit NONE.
Стоп: одна разрешённая стадия завершена; дополнительных Builds/repair нет; RESULT-CHECK-P.json проверяет отчёт и accounting, а не устанавливает полную proof acceptance.
