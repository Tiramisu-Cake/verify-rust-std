# VEIGHTMAX — кандидат v8c: v8b + принятые CITRIM, WIDEDOMAINS и TAILDIAG

**Выдано координатором 2026-11-05, решение владельца.** Dispatch только после exact-packet PRE-BUILD review/GO
координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-veightmax**, ветка **experiment/kani-k1-veightmax-20261105** от **6ef2158d9d**
  (CITRIM: library `f1ce831c2c` = v8b + 11 частей CITRIM, 226 ordinary).
- Slug **veightmax**, stable owner **k1-merge**. Request_id/stage/ledger `veightmax-*`.
- Project cap **$118.96**, свой cap **$2.00**. **Одна сборка**, retry нет. Один compile-error repair, если own spent
  + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять.
- Окно: main 180 + closeout 30 мин.

## Цель

Перенести в ordinary-набор семь уже доказанных opt-in корней и проверить на GCB, что итоговый набор компилируется
целиком и состоит ровно из ожидаемых имён. Новых доказательств и оптимизаций этот этап не делает.

Источники (наши ветки; читать их RESULT и код через `git show`):

| Источник | Корень (`verify::`) | Время G, с |
|---|---|---:|
| WIDEDOMAINS `30b4a0796a` | `widedomains::swap_safety_u8_backing32` | 33.7 |
| WIDEDOMAINS | `widedomains::swap_safety_u64_backing32` | 40.4 |
| WIDEDOMAINS | `widedomains::unstable_network_safety_u8_n32_stubbed` (consumer swap u8 backing32) | 135.1 |
| WIDEDOMAINS | `widedomains::merge_safety_u64_len8_scratch48_src32_dst0` | 80.9 |
| WIDEDOMAINS | `widedomains::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed` (consumer merge8) | 7.1 |
| TAILDIAG `59ada14d0a` | `taildiag::u64_backing17_tail1_to7_no_explicit_frame` | 31.3 |
| TAILDIAG | `taildiag::u64_backing17_tail8_to15_no_explicit_frame` | 64.2 |

Не переносить: остальные корни этих модулей (TIMEOUT, conditional consumers, `swap_safety_u64_backing32_tail_comparator`,
`merge_probe_u64_len16_network_backing32`, диагностические варианты TAILDIAG).

## Как

1. Корни — в ordinary-код (`cfg(kani)`, без `kani_smallsort_controls`): в существующий модуль контрактов
   (`verify/realcontracts.rs` или по смыслу) либо в новый модуль с нейтральным именем. Имена модулей и корней — по
   смыслу, без названий исследовательских этапов (`widedomains`, `taildiag`) и без ссылок на этапы, сборки и RESULT
   в коде библиотеки.
2. Тела, атрибуты (`proof`/`proof_for_contract`, `unwind`, `solver`, `stub`, `stub_verified`), фикстуры, компараторы
   и covers — **token-identical** доказанным версиям. Допускаются только перенос, переименование и устранение
   дублей с уже существующими хелперами, если те token-identical. Doc каждого корня — точный домен (T, F, allocation,
   start, tail/len, initialization), как в источнике. Пары PFC + consumer переносить только вместе.
3. Opt-in модули `widedomains.rs`/`taildiag.rs` в library не добавлять. Runtime `smallsort.rs`, существующие
   ordinary-корни и контроли не менять.
4. Статическая проверка (скрипт в `research/.../veightmax/`): mapping «источник → новое имя» с token-equality тел и
   атрибутов; ожидаемый ordinary-список = 226 CITRIM (`citrim/final-ordinary-expected.txt`) + 7 = **233** точных
   имени; rustfmt; diff-check.

## Сборка

Kind diagnostic, `controls: false`, **`inventory: true`**, jobs 1, gcb-e2-standard-4, лимит на корень 4 мин. Строки —
семь перенесённых корней. Ожидание: 7 SUCCESS с прежними covers; inventory без ошибок компиляции и ровно 233 ordinary
имени из ожидаемого списка. 11 частей CITRIM не перезапускать (их код не меняется).

## Коммиты

- Library-коммит и research-коммит отдельно, `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не
  опрашивать статус в цикле.
- Submission-ветку не создавать: это сделает координатор.

## RESULT

**RESULT-VEIGHTMAX.md**, ≤ 30 строк: identities; mapping и таблица 7 строк (status, время, covers); inventory
(count, совпадение со списком, hash); ordinary 233 и сумма времени новых корней; что не так, если что-то не так.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep/inventory. Raw logs, archives, Cloud Logging и
  credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Runtime `smallsort.rs`, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **VEIGHTMAX ЗАВЕРШЁН**, одна стадия, затем стоп.
