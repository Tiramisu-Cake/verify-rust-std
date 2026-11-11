# KANI3300 T1b-D — почему diagnostic_trace = INVALID (build cbf4045a), без новой сборки

**Выдано координатором 2026-11-11.** Основание: `kani3300/t1b-r/RESULT-KANI3300-T1B-A2.md`: verify выполнен, 9 verdicts = T1a,
но `diagnostic_trace state=INVALID`, `trace-field` → `pages withheld`. Runtime **Codex**, одна стадия, **Cloud $0**,
никаких Build. `TASK-KANI3300-T1B.md` и поправки планера в силе.

## Что сделать

1. Установить причину INVALID **по bounded интерфейсу** (`k1g.sh summary/native-field` для build `cbf4045a`, поля
   `summary.json.diagnostic_trace.*`: state, reason/validation errors, размеры, counts, identity) и по коду: producer —
   diagnostic delta в `/root/kani-fix-3300-t1` (989f72351c), sidecar/validator — tooling extension (`diagnostic_trace.py`,
   `k1g.sh trace-field`, c3468b3bd8). Классифицировать: (a) producer записал неверно/частично; (b) bounds сработали
   (OVERSIZED/PARTIAL ошибочно сведены к INVALID); (c) identity/env mismatch (TRACE_ID/STAGE/applied tree); (d) баг
   validator/reader. Raw archive/logs не читать; если bounded полей недостаточно — назвать точное недостающее поле.
2. Если (d) или (b) и данные sidecar в summary/архиве сборки валидны по смыслу — исправить tooling (service/error-path tests
   обязательны, существующее поведение `summary/native/native-field` не менять), независимое ревью, затем **повторно
   прочитать уже готовую сборку cbf4045a** исправленным reader'ом — без нового Build — и выписать ключевые записи
   `cmp3_index_range_len` и calibration pair.
3. Если (a)/(c) — исправление producer/env и пакет A3 только подготовить (резерв ≤ остатка $0.5975), не запускать.

## Результат

`kani3300/t1b-d/RESULT-KANI3300-T1B-D.md` (≤ 40 строк: класс причины с доказательством по полям/коду, правка, тесты, ревью,
при (d)/(b) — ключевые trace-записи). Коммит `[skip ci]`, push без force. Последней строкой `T1B-D DONE <research sha>`
(или `PRE-BUILD REVIEW <sha>`, если подготовлен A3), стоп.

## Запреты

- Никаких Build/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать, identity guard не обходить. Никаких Actions/PR/issue/комментариев, push в Kani.
  Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
