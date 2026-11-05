# TAILDIAG — почему PFC настоящего `insert_tail` не растёт дальше tail 4

**Выдано координатором 2026-11-05, решение владельца.** Dispatch только после exact-packet PRE-BUILD review/GO
координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-taildiag**, ветка **experiment/kani-k1-taildiag-20261105** от **4fa6151b6a**
  (VEIGHTINTEG: library = кандидат v8b с `requires`/`modifies` на настоящем `insert_tail`).
- Slug **taildiag**, stable owner **k1-network**. Request_id/stage/ledger `taildiag-*`.
- Project cap **$118.96**, свой cap **$2.00**. **До двух сборок** G1/G2, G2 — после разбора G1 и GO координатора.
  Retry нет. Один compile-error repair на сборку, если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять.
- Окно: main 240 + closeout 30 мин.

## Факты (всё — наши ветки, читать RESULT и код)

- v8b: PFC настоящего `insert_tail` (`realcontracts::insert_tail_safety_u64_tail1_to4_backing5`) — 34–38 с.
- WIDEDOMAINS (`30b4a0796a`): 15 PFC настоящего `insert_tail` на `[u64; 32]` / scratch 48 (tail до 19, разные
  фикстуры, полная и probe-рамка) — все TIMEOUT 3–4 мин.
- LOOPREAL (`77d9a0abb5`): с loop invariant на настоящем цикле даже backing 8 — TIMEOUT.
- При этом в ordinary v7/v8 есть `network::insert_tail_contract_u64_start1_tail{2_to8,9_to12,13_to14,15_to16}` —
  PFC **профиля** `merge::specfix::insert_tail_profile` на `[u64; 17]`, start 1, tail до 16, 160–280 с. Профиль
  отличается: канонический компаратор `LtU64` с пробой вместо произвольного ответа, `requires` с отсортированным
  префиксом, `ensures`; некоторые соседние корни используют `#[kani::solver(cadical)]`.

## Цель

Найти, какой фактор делает PFC настоящего `insert_tail` дорогим, и получить максимально широкий домен ≤ 200 с.
Если удастся дойти до tail 15 (весь путь fallback ≤ 16) — во второй сборке доказать `insertion_sort_shift_left` до
16 со `stub_verified(insert_tail)` в точно совпадающем домене.

## Что сделать (G1, ≤ 10 строк, 4 мин/корень)

Новый opt-in модуль `verify/taildiag.rs` под `cfg(kani_smallsort_controls)`. PFC настоящего `insert_tail`, факторы
менять по одному относительно базовой точки, чтобы влияние было видно:

1. **Размер backing при прочих равных:** backing 8, 12, 17 (start 0, tail произвольный в пределах), u64, компаратор с
   произвольным ответом — как в v8b.
2. **Компаратор:** тот же backing 17, но детерминированный строгий порядок по значению (по образцу `LtU64`, без
   requires сортированности — safety-контракт её не требует).
3. **Solver:** базовая точка backing 17 с `cadical` и с `kissat`.
4. **Тип:** backing 17, u8 вместо u64.
5. **Рамка:** базовая точка без явной проверки рамки вне `[begin, tail]` (её и так проверяет `modifies`).

Covers на обе ветви компаратора (где он произвольный) и на крайние tail. Каждый корень — точный домен в doc.

## G2 (только после GO)

По итогам G1 — самая дешёвая комбинация на нужных доменах, разбитая на части ≤ 200 с, и, если покрыт tail 1..15,
consumer `insertion_sort_shift_left` len ≤ 16 с `stub_verified(insert_tail)`. Домен заглушки обязан совпадать
(T, компаратор, allocation, начало); иначе consumer не засчитывается.

## Коммиты

- Library-research коммит (модуль) и research-коммит отдельно, `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не
  опрашивать статус в цикле.

## RESULT

**RESULT-TAILDIAG.md**, ≤ 40 строк: identities; таблица строк (фактор, status, время, peak RSS); какой фактор
решающий (как гипотеза, если причинность не изолирована); итоговые домены `insert_tail` и (если G2)
`insertion_sort_shift_left`; кандидаты в ordinary ≤ 200 с.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep. Raw logs, archives, Cloud Logging и credentials не
  читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Runtime `smallsort.rs`, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **TAILDIAG ЗАВЕРШЁН**, одна стадия, затем стоп.
