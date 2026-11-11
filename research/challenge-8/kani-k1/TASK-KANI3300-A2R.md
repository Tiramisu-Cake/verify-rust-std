# KANI3300 A2R — raw_eq: проверка вместо Unsupported (после узкого fork CI)

**Выдано координатором 2026-11-12.** `TASK-KANI3300-A2.md` в силе. Runtime **Codex**, одна стадия, **Cloud $0**.

## Факт: `Uninit Quick`, ветка `uninit-ci/a2-layout` (A2 `3dc0227cee`), run 43107071880

Format/build/clippy PASS; kani suite 22/22. Suite expected: 87 passed, **4 failed**:
- существующие `maybe-uninit-transmute` (ждёт `Complete - 7 successfully verified…`, получено 6/1),
  `maybe-uninit-initialized` (ждёт 8/0, получено 6/2), `maybe-uninit-partial-copy` (ждёт свой uninit `[u8; 4]`) — во всех
  лишний `Failed Checks: Kani does not support checking memory initialization of raw_eq, which reads all bytes through
  references.` — std array `==` идёт через `raw_eq`; объявлять его Unsupported слишком широко (регрессия);
- новый `raw-eq-uninit-unsupported`: вместо этого Unsupported получены `Transmuting between types of incompatible layouts.`
  ×2 и uninit `u32`.

A1 подтверждён исполнением: на неисправленной части 1 typed assignment/argument/return/array padding дают
`VERIFICATION:- SUCCESSFUL` (ложный SUCCESS), на A1 — ожидаемые FAILURE; весь узкий набор A1 зелёный (run 43105165870).

## Что сделать

1. `raw_eq` (оба операнда — ссылки на `T`, читаются все `size_of::<T>()` байт): инструментировать как проверку
   инициализированности **всех байт** обоих pointee (CheckRef/Check полного extent) — не Unsupported. Unsupported только
   там, где layout pointee нельзя вычислить. Существующие три теста должны вернуться к своим golden без правок.
2. Новый тест raw_eq переписать: (a) оба массива полностью инициализированы → SUCCESS; (b) один байт uninit → uninit FAILURE
   на raw_eq; без посторонних transmute-ошибок (разобрать, откуда в нём `Transmuting between types of incompatible
   layouts` — дефект теста или A2-кода; если A2-кода — исправить).
3. Остальную A2 (Pat offset, enum local offsets) не трогать. rustfmt `--config-path rustfmt.toml`, diff --check,
   clippy/`-D warnings` source audit, независимое ревью.

## Результат

Коммиты в `/root/kani-fix-3300-a1` поверх `3dc0227cee` (не пушить). `kani3300/a2r/RESULT-KANI3300-A2R.md` (≤ 15 строк),
research-коммит `[skip ci]`, push без force. Последней строкой `A2R READY <sha Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
