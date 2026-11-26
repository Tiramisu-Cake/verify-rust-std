# REV2 N26–N31 merge и нечётные центры · независимое ревью R1

**GO_WITH_NITS**, блокеров нет · ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26 · Std `71953c45a9a38cff3538c8a5e413890efc896d70` (tree `f59ea89d61`, parent `ea34c58ab9`), control `108c45668b1c8aa41a6f0ae228697a639ad54933` (tree `e4997c4c94ba6b0ce426f4e2fdbbb86c38de05d7`, parent `302604ce81`), review-trigger `45a580e406` (тот же tree, sole parent `467af9cb8d`), handoff g0 `26034ac432`. [Задание](REV2-N26-N31-MERGE-TASK.md) · [Handoff](REV2-N26-N31-MERGE-HANDOFF.md)

## Неблокирующее

1. `ch8-cal1/run.py:269–279`: удалена ветка `elif selector.startswith(spec.PREFIX): require(not targets)`, которая запрещала Check-объект у standard harness текущего модуля. Риск мал: точный набор (kind, selector) и дельта ровно 8 Check сохранены. Вернуть проверку `not targets` для selectors вне `*_CHECKS` в следующем пакете.
2. `results.py:227`: имя функции для локации `single_top_level_call`/`no_recursive_call` берётся из ID самого свойства. Внешнюю привязку дают regex `_checked_property` по `target_instance`, строка `modifies` и столбец 1. Этого достаточно, нужен честный комментарий.
3. Odd harness (`rev2_n26_n31_merge.rs:649`, `:761`, `:873`): `less` создаётся, но в обёртку не передаётся, поэтому `Q_FRAME` тривиален. Это унаследовано от N23/N25. Комментарий `:631` ссылается на `1027–1036`, guard стоит на `:1042` и проверяется в harness.

## Проверено

- **Std-дельта** — только check-cfg, cfg-gate (17 cfg) и новый модуль на 944 строки. Runtime и опорные blobs (`smallsort.rs` `0b77c3db`, `cal1_model` `236394dc`, `ptr/mod.rs` `9220ac5a`, `rev2_merge_pair_fixed` `b8580df3`) не изменились. Stubs, Replace, loop contracts и assume в wrapper нет. rustfmt и `git diff --check` чистые.
- **Пять pair Check** побайтно совпадают с подстановкой (N, m) в принятый шаблон FIX1 N22: аргументы, requires, modifies ровно двух целей, порядок половин только в harness, посты и 10 covers.
- **Три odd Check** — параметрические копии с транскрипцией `smallsort.rs:1027–1036`. Домен даёт остатки `{(1,0),(0,1)}`, sentinel-cover c=m, modifies только D[m].
- **Ранговая индукция** (handoff:83–89) корректна. M31-PAIR-FIXED: хэши, VERIFIED, blobs совпадают.
- **Control.** Хэши request, roster, bindings и bundle сходятся. 8 Check, `copy_back=false`, anchors, 145 нативных и 254 source-координаты, compile preflight до discovery, дельта 8, часы и caps по заданию, новая переменная, `test_supervisor.py` `df63a457`, авторство и `[skip ci]`.
- **Suite** в чистом clone: 121/121 OK.

NOT_RUN: cargo, rustc, Kani, CBMC; шкалы 1/5/60 с (у автора 121/121 на четырёх шкалах); `bundle verify` на shallow-базе (у автора PASS); YAML и `bash -n` (дельта workflow — имена и таймауты).

Решение координатора: замечания 1–3 перенести в следующий пакет (сквозной N26–N31), повторный FIX не нужен. CI свободен, пакет передаётся планеру на GO.
