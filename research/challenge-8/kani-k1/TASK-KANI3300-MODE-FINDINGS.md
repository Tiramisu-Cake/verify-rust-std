# KANI3300 MODE-FINDINGS — разбор отказов набора границы Replace/Recursive (ISSUED 2026-11-13 → worker14)

Это верификация корректности, не security-работа. Только чтение исходников и локальный Python; никаких cargo/rustc/Kani/CBMC/CI/скачиваний/push.

## Вход
- Композиция координатора: /root/kani-fix-3300-compose1, ветка compose/kani-3300-part1-c2 @ fef9e0f38
  (= 645315ec2 твои оракулы + afeee060f MARKER-MODES worker15 + fef9e0f38 docs).
- Quick CI run 43434557435: kani 22/0, expected 156/0, ui 14/0, script 1/0, json uninit-contract-oracles ok;
  json uninit-contract-mode-boundaries FAILED.
- Артефакты (уже скачаны): /root/kani3300-h1-ci/compose-c2-art/tmp.N9PEtF38v1/mode-boundary-results/
  {observations.json, <root>/{run.log, export.json, observation.json, *.rs, ...}}. Ограниченный лог CI: /root/kani3300-h1-ci/compose-c2.log.
- Фикстуры: tests/json-handler/uninit-contract-mode-boundaries/{replace.rs,recursive.rs,roots.json,run.py,README.md}.

## Наблюдения координатора (проверить)
1. recursive_check: kani-compiler `thread 'rustc' has overflowed its stack` → SIGABRT. Крах компилятора.
2. replace_ordinary (ожидался PASS как legal companion): Failed Checks —
   uninit read `&bool` в passthrough::{closure#3}::{closure#1} (replace.rs:22),
   uninit read `bool` в passthrough::{closure#3} (replace.rs:21),
   Unsupported layout для замыкания replace.rs:22:17 в apply_closure (замыкание с ненулевым захватом?).
3. replace_simple_check: те же три отказа (closure#2 вместо closure#3).
4. replace_transfer: Unsupported closure layout.

## Задачи
1. Для каждого отказа: точный источник (pass/visitor/операция), и есть ли он на upstream bf9c58e662 без Part 1
   (по коду; Kani upstream read-only клон /root/kani-upstream-3300 или аналогичный), или его вносит что-то из цепочки
   Part 1 (A1–A3R, B1I, M1, S3/M2-B 58497d98d0, CLOSURE-ZST 0ad35c0a93). Особое внимание: S3 (delayed-UB через
   registration trampoline) и рекурсия — не зацикливается ли обход body_overrides/call graph на recursive contracts
   (#[kani::recursion]) → stack overflow.
2. Что такое `bool`/`&bool`, читаемые как неинициализированные в closures контракта при ORDINARY корне:
   какой closure (requires/ensures/modifies/recursion flag), откуда shadow false, ложное ли это срабатывание.
   Если ложное и вносится Part 1 — это блокер; предложи минимальный фикс (не реализуй).
3. Ненулевое closure (захват) в ensures — подтвердить по layout/захватам; это известная граница (upvar layout).
   Совпадает ли с handoff CLOSURE-ZST про `out`.
4. Корректность самого набора: ожидания roots.json для legal companions разумны?

Результат: g0 `kani3300/mode-findings/` — FINDINGS.md (≤60 строк, по пунктам с классом: UPSTREAM / PART1-INDUCED / TEST-DESIGN / UNKNOWN,
источники file:line), коммит research [skip ci] автор Tiramisu-Cake <igkharin@gmail.com> через -c, без push. `READY <sha>`.
