# WIDEDOMAINS — safety-контракты настоящих хелперов на все реальные длины модуля

**Выдано координатором 2026-11-05, решение владельца: расширить домены контрактов.** Dispatch только после
exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-widedomains**, ветка **experiment/kani-k1-widedomains-20261105** от
  **4fa6151b6a** (VEIGHTINTEG: library = кандидат v8b, 219 ordinary; контракты `requires`/`modifies` на
  `swap_if_less`, `insertion_sort_shift_left`, `insert_tail`, `sort4_stable`, `bidirectional_merge`).
- Slug **widedomains**, stable owner **k1-merge**. Request_id/stage/ledger `widedomains-*`.
- Project cap **$118.96**, свой cap **$4.00**. **До трёх сборок** G1–G3, каждая следующая — после разбора
  предыдущей и GO координатора. Retry нет. Один compile-error repair на сборку, если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять.
- Окно: main 300 + closeout 30 мин.

## Цель

В v8b контракты доказаны PFC на узких доменах: swap backing 4/9/13, `insert_tail` tail ≤ 4, merge len 2/4,
insertion len 2/3 (opt-in, > 60 с; ordinary PFC у insertion нет). Нужно покрыть **все длины, с которыми модуль
реально вызывает эти функции** (пороги в `smallsort.rs`: ≤ 32, scratch general 48). Произвольная длина за
пределами порогов — не цель этапа.

## Порядок (по шагам; на каждом шаге — один consumer на реальном месте вызова)

1. **`swap_if_less`, backing 32**, u8 и u64; позиции `kani::any()` в backing, включая равные. Consumer:
   реальный маршрут сети с `stub_verified(swap_if_less)` на самой большой длине, которая укладывается в лимит
   (цель N32; при TIMEOUT записать максимальную прошедшую).
2. **`insert_tail`, tail до 19** (нужно для insertion N20), PFC по частям (по длине хвоста или диапазонам), каждая
   часть ≤ 200 с. Consumer: шаг 3.
3. **`insertion_sort_shift_left` до 16, затем 20** через `stub_verified(insert_tail)`: в теле остаётся цикл из
   заглушек. PFC с произвольным `offset` в пределах контракта. Если домен частей `insert_tail` не покрывает все
   вызовы — consumer не засчитывается.
4. **`bidirectional_merge` ступенями 8 → 16 → 32** под реальные места вызова (`small_sort_general` до 32,
   `sort8_stable` 8, network-merge). Широкий перебор геометрий и типов не делать.

## Требование к доменам (обязательно)

Части PFC **вместе** должны покрывать заявленный домен каждого consumer: T, компаратор F, позиции/offset/len,
allocation и frame (backing, смещение внутри allocation). Backing 32 сам по себе не покрывает scratch 48 — это
надо учесть, где хелпер работает в scratch. В RESULT для каждого consumer — явная таблица «вызовы consumer ⊆
объединение доменов PFC» с обоснованием. Kani это не проверяет; это наш аргумент, он должен быть точным.

## Код

- Новый opt-in модуль `verify/widedomains.rs` под `cfg(kani_smallsort_controls)`; регистрация одной строкой в
  `verify.rs`. Контракты в `smallsort.rs` **не менять**. Если для покрытия нужен другой `requires` — записать как
  вопрос координатору, не менять самостоятельно.
- Каждый корень ≤ 200 с на GCB — кандидат в ordinary; что дольше — факт для RESULT.
- Covers на ветви ответа компаратора и на достижение крайних длин.

## Сборки

Kind diagnostic, `controls: true`, jobs 1, gcb-e2-standard-4, `harness_timeout_minutes` минимальный разумный
(≤ 10). G1 — шаги 1 и часть 2; дальше по итогам. ≤ 10 строк на сборку.

## Коммиты

- Library-research коммит (новый модуль) и research-коммит отдельно, `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не
  опрашивать статус в цикле.

## RESULT

**RESULT-WIDEDOMAINS.md**, ≤ 45 строк: identities; таблица строк по сборкам; таблица покрытия доменов для
каждого consumer; итоговые домены пяти контрактов «было → стало»; кандидаты в ordinary (≤ 200 с) с добавкой к CI;
что осталось.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep. Raw logs, archives, Cloud Logging и credentials не
  читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Runtime `smallsort.rs`, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **WIDEDOMAINS ЗАВЕРШЁН**, одна стадия, затем стоп.
