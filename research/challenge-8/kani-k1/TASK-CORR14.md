# CORR14 — пилот: split маршрутов и форма stable scratch на `correct` u8 N14

Дата: 2026-10-31. Исполнитель: Codex, одна свежая сессия, окно до 4 ч (3,5 ч работа + 0,5 ч закрытие; основное
время — ожидание сборок). Worktree `/root/verify-rust-std-kani-corr14` (сессия может быть открыта в `/root` — работать
только в этом worktree, `cd` в него), ветка `experiment/kani-k1-corrfourteen-20261031` от `e6a8ad05c9` (итог ASSEMBLY, library
`d4e5a0907b`, CI организаторов зелёный). **Бюджет Cloud Build: не более $2,3 и не более 2 сборок** (свой список build
UUID/request_id; agent label общий и расходы не разделяет), пул k1-standard4; `CAP_USD 73.96` не менять; перед каждой
сборкой `k1g.sh budget` и полный envelope + резерв закрытия в остатке окна. Сборку ждать **только через
`k1g.sh watch BUILD` и завершать ход**. Результаты своих сборок — штатно через `k1g.sh
summary/peaks/inventory/log-grep/log-lines/check-tooling`; Evidence Brief и процедуры Select/Merge не применяются.
Pin Kani `9461e07a`, toolchain, flags, lane-файлы не менять. Actions/CircleCI — нет. Ветки `submission/*` не трогать.
Параллельно работают пилоты M9 (`merge.rs`) и START1 (`network.rs`): **писать только `verify/correct.rs`**.

## Зачем

`correct::general_stable_stub` (N13..15) — одно из самых тяжёлых семейств Part 2: symbolic `stable` держит в одной
формуле оба маршрута, stable-ветвь создаёт non-const `[MaybeUninit::<T>::uninit(); 48]`; insert_tail и merge — через
`stub_verified`, sort4 реальный. Историческая подсказка C3c: general-only N14 112 с / 1,23 GiB против combined 304 с /
2,13 GiB (source/covers менялись — не matched speedup). На u64 N8 aggregate scratch снизил RSS stable в 5 раз
(BACKING); механизм не установлен. Цель — matched на u8 N14: эффект split и эффект формы scratch по отдельности.

## Что сделать

Все новые helper-ы/гармоники — private opt-in (`cfg(kani_smallsort_controls)`); существующие символы не менять.
Сохранить: `set_value_probe`, произвольный input, тот же inline oracle (sortedness + `probe_count_unrolled`), тот же
`lt_u8`, `stub_verified(insert_tail)` и `stub_verified(bidirectional_merge)`, solver cadical, unwind 50.
1. Entry 1 — существующий combined `sorted_permutation_general_stable_u8_n14` (baseline, без изменений).
2. Entry 2 — только `small_sort_general` (без symbolic `stable`), cover на возврат.
3. Entries 3–5 — только `StableSmallSortTypeImpl::small_sort` с формой scratch: non-const (как сейчас), const
   (`[const { MaybeUninit::<u8>::uninit() }; 48]`), aggregate (`MaybeUninit<[u8;48]>` + свой private adapter в
   `correct.rs` по образцу `merge::scratch_view` — тот private, его не трогать; SAFETY: provenance, alignment,
   extent 48, exclusivity, lifetime; только `&mut [MaybeUninit<T>]`, без `assume_init`). По helper-у на форму, без
   скрытого selector. Статически показать: general + non-const stable воспроизводят прежние ветви/входы combined; const и
   aggregate сохраняют функциональный T/F/N/input/probe-домен, но aggregate — другая backing-геометрия (не
   доказательство старой fixture и не transfer). Fixed-route covers объединяются; отдельная гармоника не обязана
   покрывать противоположный маршрут.
4. Два контроля на новой копии adapter (opt-in, ожидаются FAILED, location сверять вручную): (а) после stable sort
   на aggregate-форме `output[0] ^= 1` перед тем же full-value count-assert (`lt_u8` сравнивает `x >> 1`, младший
   бит — payload, sortedness сохраняется) → единственный FAILED — count-assert; actual `lt_u8` и оба stub targets
   сохранить, новый comparator/closure не вводить; (б) bounds: raw write one-past всей allocation 48 через указатель
   adapter → Kani memory/object-bounds failure (не safe indexing panic, не чтение uninit T). Precondition-контроль
   — только факультативно третьим, не вместо bounds. Inline asserts без сообщений: Kani покажет
   placeholder — expect_check `This is a placeholder message` + ручная сверка location.
5. Ускорение conditional caller не закрывает callee premises (`insert_tail`/`merge` контрактов на этих
   доменах) — записать явно; N15 в этой сессии не добавлять.

## Сборки

Перед первой: commit + push кандидата, последней строкой хода `PRE-BUILD REVIEW <sha>`, завершить ход; ждать GO
координатора. До dispatch записать T0 и резерв закрытия.
1. `measurement`, jobs=1, controls:true: 5 positive + 2 контроля = 7 entries, envelope 100 мин ≈ $1,35.
2. Только при пользе — обе выбранные ветви (general и лучшая stable) SUCCESS, covers SATISFIED, контроли целевые,
   измеренный выигрыш пика или суммарной цены (решать по строкам, не по aggregate gate; условность caller не
   снимается): `diagnostic`, `kani_jobs: 3`, `controls:true`: general N14, лучшая stable N14,
   `correct::contract_insert_tail_u8_scratch`, `merge::merge_contract_u8_n14` — 4 entries, 70 мин ≈ $0,945
   (ресурсная проверка листьев, не transfer на scratch48 caller).
Library tree для G1/G2 заморозить; request SHA/UUID связывать с точным tree, `check-tooling` и expected names.
Timeout 600 не менять; TIMEOUT/OOM — тоже данные.

## Результат

`research/challenge-8/kani-k1/RESULT-CORR14.md` (русский, ≤ 100 строк): SHA, build ID, стоимость; COMPLETE / PARTIAL
/ STOP; таблица (гармоника, маршрут, форма scratch, статус, VT, CBMC RSS, covers, checks); вывод отдельно по split и
по форме scratch; контроли с location; jobs=3; рекомендация для N13/N15 и u64 (не запускать); оговорки (conditional
caller, fixture48 ≠ любой backing; macOS UNKNOWN; пригодность — только CI организаторов).
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
CORR14 ЗАВЕРШЁН
```
После маркера сессию не продолжать.
