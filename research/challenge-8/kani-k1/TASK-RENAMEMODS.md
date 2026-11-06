# RENAMEMODS — понятные имена модулей и сообщений вместо внутренних кодовых имён

**Выдано координатором 2026-11-06, решение владельца.** Четвёртый этап очистки перед подачей Part 1.
Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-renamemods**, ветка **experiment/kani-k1-renamemods-20261106** от
  **d44afad690** (LEANHELPERS PASS: library `5c929ba094`, tree `ed9d8de3a0`; 233 ordinary + 13 контролей).
- Slug **renamemods**, stable owner **k1-merge**. Request_id/stage/ledger `renamemods-*`.
- Project cap **$118.96**, свой cap **$1.20**. **Одна сборка**; G2 — только для исправления нашей ошибки после GO.
  Retry нет. Один compile-error repair, если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять.
- Окно: main 240 + closeout 30 мин.

## Цель

Имена модулей проверки — кодовые имена этапов разработки; ревьюер upstream видит их в полном имени каждого корня.
Переименовать **один к одному** (без слияния и разделения файлов) по утверждённой владельцем таблице:

| Сейчас | Новое имя |
|---|---|
| `verify/merge/specfix.rs`, `merge::specfix` | `verify/merge/profiles.rs`, `merge::profiles` |
| `verify/permtags.rs` | `verify/tag_permutation.rs` |
| `verify/scratchgeom.rs` | `verify/scratch_geometry.rs` |
| `verify/assembly.rs` | `verify/fixed_inputs.rs` |
| `verify/wrap.rs` | `verify/forwarding_contracts.rs` |
| `verify/realcontracts.rs` | `verify/helper_contracts.rs` |
| `verify/allocationcontracts.rs` | `verify/helper_contracts_wide.rs` |
| `verify/tailcontracts.rs` | `verify/insert_tail_contracts.rs` |

Файлы переносить через `git mv`. Обновить все `mod`, `use`, пути в атрибутах (`proof_for_contract`,
`stub_verified`, `stub`) и комментарии/карту в `verify.rs`.

Дополнительно:
1. **Идентификаторы `specfix_*` → `profile_*`**: `specfix_canonical_comparator` и пять контролей
   (`specfix_full_value_checker_rejects_payload_change_u8`, `specfix_wrong_f_{swap,sort4,insert,merge}_rejected_*`).
2. **Сообщения `assert!`/`kani::assert`/`kani::cover`**, которые начинаются с имени модуля («specfix …»,
   «permtags: …», «realcontracts …», «wrap …» и т. п., около 64): убрать префикс модуля или заменить его описанием
   свойства, чтобы сообщение читалось само по себе. Не менять число и место проверок и covers; не делать два
   разных сообщения одинаковыми, если они были различны.
3. Найти grep'ом прочие идентификаторы/строки/комментарии с этими восемью кодовыми именами в `verify.rs`,
   `verify/**` и комментариях `smallsort.rs`; переименовать, если это не меняет ничего, кроме имени. Список
   оставшихся (если есть) — в RESULT с причиной.

**Нельзя:** менять тела, атрибуты (кроме путей модулей), длины, типы, covers, `unwind`, solver; объединять или
делить файлы; менять имена корней кроме модульного префикса и `specfix_*` контролей; менять код `smallsort.rs`
(только комментарии, если там упоминаются старые имена).

## Статические проверки (скрипт в `research/challenge-8/kani-k1/renamemods/`)

Переиспользовать лексер/expander из `leanhelpers/check_leanhelpers.py`.
- Явная таблица соответствия старых и новых полных имён: 233 ordinary и 13 контролей, биекция, без потерь и
  дубликатов; файлы `ordinary-expected.txt` и `cfg-on-expected.txt` с новыми именами.
- После обратной подстановки (новые имена модулей/идентификаторов → старые, новые тексты сообщений → старые по
  таблице) раскрытые items всех 246 корней и их замыкания **токен-идентичны** LEANHELPERS `5c929ba094`.
- Число и место `kani::cover` у каждого корня не изменились; все тексты сообщений внутри одного корня
  по-прежнему попарно различны там, где были различны.
- `rustfmt --check` (обёртка
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --edition 2024 --config-path
  research/challenge-8/kani-k1/codefix/rustfmt.toml library/core/src/slice/sort/shared/smallsort.rs`) — ноль diff.
- Строк > 100 нет. Поиск восьми старых имён (и `specfix`) в `verify*` и комментариях `smallsort.rs` — пусто,
  кроме перечисленных в RESULT исключений. Запрещённая лексика TIDYDOCS — пусто.

## Сборка G1

kind inventory, `controls: false`, standard4, без proof-строк: компилятор должен выдать ровно 233 новых
ordinary-имени (сравнить отсортированный SHA256 с `ordinary-expected.txt`), без новых предупреждений в
`smallsort/verify`. Лимит сборки рассчитать по OPTINMOVE G1 (тот же kind: ~42 мин). Cfg-on (246) и прогон
13 контролей — в интеграционном пакете после этого этапа.

## Коммиты

- Library-коммит(ы) и research-коммит отдельно, `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не опрашивать
  статус в цикле.

## RESULT

**RESULT-RENAMEMODS.md**, ≤ 30 строк: identities (library SHA и tree); статика; inventory (число, SHA256);
ссылка на таблицу соответствия имён; сколько сообщений изменено; оставшиеся упоминания старых имён (если есть);
расход.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep/inventory. Raw logs, archives, Cloud Logging и
  credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC (rustfmt разрешён), Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Workflows, скрипты и tooling не менять. Код `smallsort.rs` не менять.

Маркеры `REVIEW REQUEST <sha>` / **RENAMEMODS ЗАВЕРШЁН**, одна стадия, затем стоп.
