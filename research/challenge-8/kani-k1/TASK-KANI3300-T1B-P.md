# KANI3300 T1b-P — прототип «свежий BodyTransformation на root» + пакет P (3 roots), подготовка

**Выдано координатором 2026-11-11.** Рамки — планер: `kani3300/t1b-p/PLANNER-T1B-C2-ANSWER.md` (прочитать целиком,
п.3–6 обязательны). Основание: `kani3300/t1b-c2/RESULT-KANI3300-T1B-C2.md`, `kani3300/t1b-s/STATIC.md`.
Runtime **Codex**, одна стадия, **Cloud $0**. Dispatch **не** в этой стадии: нужен новый бюджет владельца (pilot cap $0.50).

## Что сделать

1. Cache invariant (≤ 10 строк в `kani3300/t1b-p/DESIGN.md`): что должно быть общим на unit (только root-независимые
   локальные трансформации), что root-scoped (результаты global passes, reachability, тела для GOTO emission).
2. **Прототип** отдельным коммитом в `/root/kani-fix-3300-t1` поверх диагностики 12b4137c42: свежий `BodyTransformation`
   на каждый root (те же unit/stubs/config/global passes), живущий до конца GOTO emission этого root; warmup/ordering —
   на отдельном transformer или без сохранения глобально изменённого состояния. Ordering algorithm, library, flags,
   диагностику не менять; ordinary/constant transfer не трогать; CheckRef не отключать, seed не добавлять.
3. Ревью точной дельты (свой ревьюер): изоляция полная (никакой глобальной записи в общий cache), семантика local passes
   не изменена, нет утечки через auxiliary maps. rustfmt (`--config-path rustfmt.toml`), diff --check, `-D warnings`
   source audit, сигнатуры. Компиляцию проверит координатор в fork CI.
4. Пакет **P**: ровно три roots C2 (`cmp3_into_iter_next`, `cmp3_index_range_len`, `cmp3_manually_drop_unsized_len`),
   те же фильтры/timeout 1m/один invocation; резерв (3+30)×$0.0135 = **$0.4455**, pilot cap **$0.50** (stage
   `kani3300-t1b-pilot`, отдельный ledger). Критерии приёмки — п.4 планера (порядок next→manual→index; next сохраняет свои
   CheckRef; index/manual не получают чужой last_writer; index → SUCCESS, manual/next SUCCESS; сверка consumed len hash).
   Combined patch — по образцу C2 (без исторических тестов; diffstat ≤ 4096 B; check_packet.py PASS).

## Результат

`kani3300/t1b-p/`: `DESIGN.md`, `PRE-BUILD.md` (≤ 30 строк), `RUN-REQUEST-P.json`, review. Коммиты `[skip ci]`, push без
force. Последней строкой `PRE-BUILD REVIEW <research sha>` и `KANI PROTO <sha Kani>`, стоп.

## Запреты

- Никаких Build/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
