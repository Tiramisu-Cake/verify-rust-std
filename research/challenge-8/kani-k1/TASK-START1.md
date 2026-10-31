# START1 — пилот: контракт insert_tail при begin=1, полный partition по tail

Дата: 2026-10-31. Исполнитель: Codex, одна свежая сессия, окно до 4 ч (3,5 ч работа + 0,5 ч закрытие; основное
время — ожидание сборок). Worktree `/root/verify-rust-std-kani-start1` (сессия может быть открыта в `/root` — работать
только в этом worktree, `cd` в него), ветка `experiment/kani-k1-startone-20261031` от `e6a8ad05c9` (итог ASSEMBLY, library
`d4e5a0907b`, CI организаторов зелёный). **Бюджет Cloud Build: не более $2,2 и не более 2 сборок** (свой список build
UUID/request_id; agent label общий и расходы не разделяет), пул k1-standard4; `CAP_USD 73.96` не менять; перед каждой
сборкой `k1g.sh budget` и полный envelope + резерв закрытия в остатке окна. Сборку ждать **только через
`k1g.sh watch BUILD` и завершать ход**. Результаты своих сборок — штатно через `k1g.sh
summary/peaks/inventory/log-grep/log-lines/check-tooling`; Evidence Brief и процедуры Select/Merge не применяются.
Pin Kani `9461e07a`, toolchain, flags, lane-файлы не менять. Actions/CircleCI — нет. Ветки `submission/*` не трогать.
Параллельно работают пилоты M9 (`merge.rs`) и CORR14 (`correct.rs`): **писать только `verify/network.rs`**.

## Зачем

`network::insert_tail_contract_u64_start1` (`network.rs`, `insert_tail_value::<START>` + `insert_tail_contract_case!`)
— один из трёх известных блокеров Part 2: в autoharness П-6 TIMEOUT 600, C3c-проба памяти около 2,85 GiB. Гармоника
держит в одной формуле все tail ∈ 2..16. Историческая подсказка C3c: exact-tail варианты SUCCESS за 9–48 с при RSS
0,15–0,92 GiB (старый source/helpers — не proof для этого SHA). Цель — закрыть домен START1 тремя PFC,
объединение которых **ровно** равно исходному домену.

## Что сделать

1. Новый private opt-in helper рядом с `insert_tail_value`: тот же код, но tail выбирается как
   `kani::any_where(|&t| LO <= t && t <= HI)`; статические ограничения (const-assert) `START == 1`,
   `START < LO && LO <= HI && HI < 17` (const generics — без скрытого selector). Sorted-prefix предпосылок сверх
   actual PFC requires не добавлять.
   Сохранить: backing `[u64; 17]`, `set_value_probe`, START = 1, `lt_u64`, `proof_for_contract(insert_tail)` с его
   requires (sorted prefix), обе frame-проверки (prefix до begin и suffix после tail), cover «insertion moves elements»
   и cover достижимости каждого tail группы. Существующие `insert_tail_value`/`insert_tail_contract_case!` и прочие
   символы не менять.
2. Три PFC: tail 2..=8, 9..=12, 13..=16 (имена по образцу, напр. `insert_tail_contract_u64_start1_tail2_to8`).
   Статически показать в отчёте, что объединение = {2..16}, пересечений нет, START/backing/requires/frame те же.
   Исходный `insert_tail_contract_u64_start1` оставить opt-in как baseline.
3. Два контроля (opt-in, ожидаются FAILED, location сверять вручную по summary), оба обязательны: (а) prefix —
   после вызова записать в `v[0]` (begin = 1) → отказ prefix-frame assert; (б) suffix — фиксированный tail < 16
   (например 15), запись в `v[tail + 1]` → отказ suffix-frame assert (при tail 16 suffix пуст, запись в 17 дала бы
   OOB, а не frame-отказ). Контроли используют те же frame-asserts, что positive group-helper (общий checker или
   проверенная идентичность кода; независимая копия не годится), и свой достижимый cover перед намеренной порчей; все
   tail-covers группы от них не требуются. Иной класс отказа/compile error контроль не закрывает. Precondition-контроль
   — только факультативно третьим, не вместо frame-контролей.

## Сборки

Перед первой: commit + push кандидата, последней строкой хода `PRE-BUILD REVIEW <sha>`, завершить ход; ждать GO
координатора. До dispatch записать T0 и резерв закрытия.
1. `measurement`, jobs=1, controls:true: baseline START1 + 3 group-PFC + 2 контроля = 6 entries, envelope 90 мин ≈
   $1,215. В request baseline имеет `expect: SUCCESS` (lane не допускает
   `expect: TIMEOUT`); его TIMEOUT — отрицательный результат и может сделать aggregate gate false. Gate решать **по
   строкам**: три группы SUCCESS ≤ 600 с со всеми tail covers и два контроля FAILED на нужных locations.
2. Только при успехе gate: `diagnostic`, `kani_jobs: 3`, `controls:true`: три group-PFC + ordinary
   `network_safety_unstable_u64_n0_to17` (макс. VT Part 1 на macOS) — 4 entries, 70 мин ≈ $0,945. Реальное
   перекрытие CBMC, пики, OOM/missing; это Linux 16 GiB, не macOS.
Timeout 600 не менять. Если группа TIMEOUT — partial; не выдавать неполный partition за START1. Допустимо одно
дробление группы-неудачника во второй сборке вместо diagnostic — только как committed delta + review/GO координатора,
с доказательством полноты нового partition и совместимости reuse G1; больше 4 entries — новый расчёт envelope.
Library tree для каждого build заморозить; request SHA/UUID связывать с точным tree, `check-tooling`, expected names.

## Результат

`research/challenge-8/kani-k1/RESULT-START1.md` (русский, ≤ 100 строк): SHA, build ID, стоимость; COMPLETE / PARTIAL
/ STOP; таблица (гармоника, tail-группа, статус, VT, CBMC RSS, covers, checks); доказательство полноты partition;
контроли с location; jobs=3; кандидаты на замену START1 в Part 2 (и, если очень дёшево, — в Part 1, с оговоркой);
оговорки (exact `[u64;17]`, START1 не равен START0/scratch17/48; macOS UNKNOWN; пригодность — только CI организаторов).
Rustfmt:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <изменённые .rs>`
— exit 0; строки ≤ 100; без новых предупреждений в обеих cfg.

## Ограничения

- Все коммиты `[skip ci]`; library-коммиты отдельно от `research/`. Push без force. Локально только Python и rustfmt;
  rustc/cargo/Kani/CBMC — нет. Логи — только summary/peaks/log-grep/log-lines (≤ 200 строк).
- Код, ветки и аудиты PR #576/#678/#694/#701 не открывать. Не упоминать rust-lang issues. Внешних действий нет.
  Спорное решать самому, владельца не ждать.

## Завершение

Commit + push. Последние строки ответа координатору:

```
REVIEW REQUEST <sha>
START1 ЗАВЕРШЁН
```
После маркера сессию не продолжать.
