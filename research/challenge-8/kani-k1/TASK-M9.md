# M9 — пилот: прямой u64 N9 (general + stable) и триада формы stable scratch

Дата: 2026-10-31. Исполнитель: Codex, одна свежая сессия, окно до 4 ч (3,5 ч работа + 0,5 ч закрытие; основное
время — ожидание сборок). Worktree `/root/verify-rust-std-kani-m9` (сессия может быть открыта в `/root` — работать
только в этом worktree, `cd` в него), ветка `experiment/kani-k1-mnine-20261031` от `e6a8ad05c9` (итог ASSEMBLY, library
`d4e5a0907b`, CI организаторов зелёный). **Бюджет Cloud Build: не более $2,3 и не более 2 сборок** (свой список build
UUID/request_id; agent label общий и расходы не разделяет), пул k1-standard4; `CAP_USD 73.96` не менять; перед каждой
сборкой `k1g.sh budget` и полный envelope + резерв закрытия в остатке окна. Сборку ждать **только через
`k1g.sh watch BUILD` и завершать ход**. Результаты своих сборок — штатно через `k1g.sh
summary/peaks/inventory/log-grep/log-lines/check-tooling`; Evidence Brief и процедуры Select/Merge не применяются.
Pin Kani `9461e07a`, toolchain, flags, lane-файлы не менять. Actions/CircleCI — нет. Ветки `submission/*` не трогать.
Параллельно работают пилоты START1 (`network.rs`) и CORR14 (`correct.rs`): **писать только `verify/merge.rs`**.

## Зачем

Прямые u64 N6..8 (без merge-stub) в Part 1 и прошли CI организаторов (macOS VT: general 32/71/84 с, stable
19/33/102 с). N9 — первая длина с нечётными половинами merge 4/5 и одним insertion-tail шагом; сейчас домен N9 закрыт
только conditional stubbed caller `general_stable_sorted_permutation_u64_n9` (Part 2). Успех обеих прямых ветвей N9
позволит заменить его. Заодно — различить, откуда выигрыш BACKING (stable u64 N8: RSS 7,93 → 1,51 GiB при переходе с
`[MaybeUninit::<u64>::uninit(); 48]` на aggregate `MaybeUninit<[u64;48]>` + `scratch_view`): от non-const
initializer или от aggregate-представления. Механизм не установлен.

## Что сделать

1. **General N9:** `general_direct_u64_n9` через существующий `general_direct_u64_properties` — единственное
   разрешённое изменение ordinary helper — расширить const-guard до 6..=9 (тело неизменно). Гармоника — opt-in
   (`cfg(kani_smallsort_controls)`), в ordinary переводит координатор.
2. **Stable N9, три формы scratch** (opt-in), всё прочее идентично `stable_direct_u64_properties` (тот же
   `StableSmallSortTypeImpl::small_sort`, input/probe, `lt_u64`, oracle `assert_sorted_and_probe_preserved`, unwind 34,
   один cover):
   - aggregate: существующий `stable_direct_u64_properties` (guard до 6..=9);
   - non-const: `let mut scratch = [MaybeUninit::<u64>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];`;
   - const: `[const { MaybeUninit::<u64>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN]`.
   Для non-const/const — новые private opt-in helper-ы (по одному на форму, без скрытого `kani::any()` selector).
3. **Страховка триады:** stable **N8 const** (тот же helper const-формы). Опоры N8 — matched пара BACKING (source
   `740d22674c`, build `b07fdcd8-fbd8-401e-9948-9e5f9e7201ad`): non-const 292,468 с / 7,928 GiB, aggregate 214,316 с /
   1,508 GiB. (У OPT G2 то же non-const имя — 298,924 с / 7,932 GiB, source `c81c10e306`; identity не смешивать.) Опоры
   исторические, не matched этого SHA — ссылаться, не перемерять. Неудача N9 не отменяет отдельного результата S8 const.
4. Имена — по образцу соседних (`general_direct_u64_n9`, `stable_direct_u64_n9`, `stable_direct_nonconst_u64_n9`,
   `stable_direct_const_u64_n9`, `stable_direct_const_u64_n8` или лучше по смыслу); комментарии — по бюджету соседних, без
   истории разработки. Контроли: oracle и adapter не меняются. ASSEMBLY G3 проверил прежние helper/oracle на library
   `d4e5a0907b`; их неизменность и вызов из новых harness проверить source audit (это не measurement controls нового
   SHA) — новые controls не нужны. Сохранить полный arbitrary input/probe, snapshot до сортировки, тот же comparator и
   cover после assert; если меняется что-либо, кроме guard и новых helper-ов формы scratch, — нужен контроль и
   delta-review.

## Сборки

Перед первой: commit + push кандидата, последней строкой хода `PRE-BUILD REVIEW <sha>`, завершить ход; ждать GO
координатора. До dispatch записать T0 и резерв закрытия.
1. `measurement`, jobs=1, controls:true: G9, S9 aggregate, S9 non-const, S9 const, S8 const — 5 entries, envelope
   80 мин ≈ $1,08. Gate: SUCCESS ≤ 600 с, cover SATISFIED, пики CBMC/driver.
2. Только если G9 и хотя бы одна форма S9 SUCCESS с covers (решать по строкам, не по aggregate gate: TIMEOUT иной
   формы может сделать gate false; это не выдавать за полную триаду): `diagnostic`, `kani_jobs: 3`, `controls:true`: G9, лучшая S9, ordinary
   `general_direct_u64_n8`, `stable_direct_u64_n8` — 4 entries, 70 мин ≈ $0,945. Проверить реальное перекрытие CBMC
   (меньше 3 — не подтверждение), пики, OOM/missing. Это Linux 16 GiB, не сертификация macOS.
Library tree для G1/G2 заморозить (без semantic delta); request SHA/UUID связывать с точным tree, `check-tooling` и
expected names. Timeout 600 не менять; TIMEOUT/OOM — тоже данные. Если N9 TIMEOUT — partial; одну ветвь вместо обеих не предлагать.

## Результат

`research/challenge-8/kani-k1/RESULT-M9.md` (русский, ≤ 100 строк): SHA, build ID, стоимость; COMPLETE / PARTIAL /
STOP; таблица (гармоника, форма scratch, статус, VT, CBMC RSS, covers, checks); вывод по триаде (N8 и N9 отдельно;
историческая опора ≠ matched); jobs=3; кандидаты в ordinary и предложение по замене C N9 (условие — обе ветви
SUCCESS); оговорки (fixture48 ≠ любой backing; macOS UNKNOWN; пригодность — только CI организаторов).
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
M9 ЗАВЕРШЁН
```
После маркера сессию не продолжать.
