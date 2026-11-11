# KANI3300 T1b-D — RESULT
Задание 19a808200ac40a07754ba15bc4ef44eb1c92d5cb; одна стадия, Cloud $0, Builds/dispatch/локальные compiler/verifier NOT_RUN.
Build cbf4045a-cf4b-4ac7-8495-dfafcf57f6fb повторно прочитан только bounded k1g.sh; EVIDENCE-INDEX.json содержит ответы/receipts/SHA256.
Класс (d), связанный с (b): подтверждён дефект validator — смешение единиц omissions; полная валидность фактического sidecar UNKNOWN.
Фактическая errors[0]: `kani3300-trace-0.jsonl: footer coverage does not bind emitted event count`.
state=INVALID, complete=false, sidecar_bytes=254669 (<256000 producer cap); один sidecar status=READ, SHA256 7e399e510aa70d0ab55b3c9928f42bba8db277b7a8ad9c3955e4c3f7e88f6182.
Summary seen=4477/emitted=0/omitted=4477, coverage=[]; это агрегаты после отбрасывания, не исходные footer counters/полнота producer.
Head bddfa044cbb4e884f9140b51c0cc0b9dfc464e58, request73903bb3f80c34492d575d40d74a4552e4e2d9a55149e578fe05dde01d55035e — MATCH.
TRACE_ID=request SHA, STAGE=kani3300-t1b; library919cc3e2dc5fb19ea6e7f7be761914b949160a41 и applied53927d9bc0ccbff8183aa91ffb6c29d1c8a74465 — MATCH.
Env/argv/filter/tooling digests и source schema/stage прошли прежние identity checks; признаков класса(c) нет.
Producer989f72351c trace.rs:write_record считает omitted_records и категории record_cap/oversized_records вместе.
trace.rs:mark_omission отдельно считает excerpt/clipped bytes, selected lines, witnesses и payload ops; эти единицы не суммируются с числом записей.
Validator c3468b3bd8 требовал sum(всех omission_counts)==omitted_records; синтетический корректный PARTIAL воспроизводит ту же ошибку.
Правка6646181d23377325d9893b9f08e173f32c766f8c: allowlist validation.* метаданных после всех identity/envelope checks; INVALID payload закрыт.
Правкаf34c6316ef714802e93106e16c2e7e1612b2bdfd: сравнивать только record_cap+oversized_records; сохранять остальные counts/type checks и запрет COMPLETE с omissions.
summary/native/native-field, producer, активные requests/ledgers/исторические evidence не изменены; Kani989f72351c остаётся clean, без push.
Тесты: Python -I diagnostic/service13/13; прежние NativeTests+NativeFieldPageTests15/15; diff --check PASS; детали TESTS.json.
Проверены mixed PARTIAL/OVERSIZED, original exit0/1, bad counters/null/bool/negative, ложный COMPLETE, opt-out/missing/timeout, bounds и identity mismatches.
Независимое Luna HIGH review обеих committed delta: PASS, без blocking findings; REVIEW-ACCESSOR.md / REVIEW-VALIDATOR.md и identities рядом.
Повторное чтение после review: validation.errors exit0; records exit2 `diagnostic trace state INVALID; pages withheld` — guard сохранён.
Старый summary immutable: collect_trace отклонил sidecar ДО all_records.extend и coverage.append; исправление parser не восстанавливает отброшенное.
Upload recipe gcb-k1.sh:335–340 сохранял summary и выбранные log-файлы, не trace sidecar; иных архивов не проверяли.
Недостаёт bounded footer state/emitted_records/omitted_records/coverage/omission_counts и payload kani3300-trace-0.jsonl с указанным SHA256.
Точный failed subpredicate составной footer-проверки и исходное PARTIAL/OVERSIZED остаются UNKNOWN без этих полей; raw fallback не применялся.
Ключевые trace-записи cmp3_index_range_len и calibration uninit/init: UNKNOWN, восстановленных записей нет.
Bounded summary подтверждает прежние verdicts: cmp3_index_range_len FAILED2/28, calibration uninit FAILED1/30, init SUCCESS0/31; это не trace evidence.
A3 не готовился: producer/env defect не установлен; новый Build/пакет B/Cloud не разрешены этой стадией.
Independent proof credit NONE; concrete object/offset/R и runtime-причинность UNKNOWN. Стоп на документированной границе доступности evidence.
