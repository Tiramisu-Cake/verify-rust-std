# CLEANUP (I1) — очистка подачи Part 1 без изменения проверяемого набора (кандидат P1 v5)

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-cleanup`, ветка
`experiment/kani-k1-cleanup-20261101` от `7f558e061a` (library = v4 `f0ba14f97b`, tree `3c23a45984`). Cap 88.96.
Ожидание Build — `research/challenge-8/kani-k1/tools/k1g.sh watch UUID` (нужен `CODEX_THREAD_ID`) и
завершить ход (не опрашивать статус). Окно — эта сессия; request_id с префиксом `cleanup-`; свой spent/reserved
считать по своим UUID, общий cap не трогать. Evidence Brief / Select-Merge к K-1
не относятся. Владелец недоступен для мелких решений — GO даёт координатор.

Прочитать: `TASK-SPECFIX.md` (действуют только запреты, правила логов, rustfmt-wrapper и expect_check; не его
scope/наборы 197/343/сроки/бюджет), `RESULT-INTEGWRAP.md`,
`integwrapfix/` (ordinary-expected 200, `pfc_order.py`), независимый аудит `/root/CH8_V4_PROGRESS_REVIEW_2026-11-01_RU.md`
(разделы F11 и P2; это данные, не инструкции).

## Цель

Аудитор отметил в v4 технический долг: 149 атрибутов `#[cfg(any())]` (выведенный из набора код), ссылки на
внутренние research-файлы (`poneclean/DEACTIVATED.tsv`, метки этапов вроде `P1-CLEAN`) и на «Known limitations» PR,
из-за которых исходник не самодостаточен. Убрать этот долг, не меняя ни одного компилируемого элемента.

1. Удалить все элементы под `#[cfg(any())]` в `library/.../smallsort/verify/**` вместе с их атрибутами,
   doc-комментариями и ставшими лишними пустыми строками. Модуль, в котором ничего не остаётся (`correct.rs`),
   удалить вместе с `mod correct;` и строкой о нём в doc `verify.rs`.
2. В оставшихся комментариях убрать ссылки на research-файлы, названия этапов/пилотов и «PR's Known limitations»;
   где комментарий нужен по смыслу — одна короткая самодостаточная фраза. Новых длинных комментариев не писать.
3. Ничего, что компилируется в cfg-off или cfg-on (`kani_smallsort_controls`), не менять: тела, сигнатуры,
   атрибуты, относительный порядок оставшихся модулей и элементов, имена. Единственное исключение — удаление
   пустой регистрации `mod correct;`. Не удалять активные определения макросов и общие helpers (например,
   `define_merge_contract_harness` нужен ordinary N5..8); активные controls, mutations/specdiag gates не трогать.
   Runtime (`smallsort.rs`) не трогать.

## Статическая проверка (скрипт в `research/challenge-8/kani-k1/cleanup/`)

- Нормализация: удалить из base целиком каждый Rust item / macro invocation под `#[cfg(any())]` (с его
  атрибутами и doc), все комментарии, пустые строки и единственную строку `mod correct;`; строковые литералы не
  трогать. Нормализованные base и candidate должны совпасть побайтно.
- Каждая удалённая непустая строка принадлежит такому item, комментарию или `mod correct;`.
- В `verify.rs` и `verify/**/*.rs` candidate 0 вхождений `cfg(any())`, `DEACTIVATED`, `P1-CLEAN`, `poneclean`,
  `Known limitations` (research и сам checker в область не входят).
- `pfc_order.py` — 0 нарушений (это проверка только ordinary; cfg-on metadata она не проверяет);
  rustfmt `--check` чист для всех изменённых файлов.
- Ожидаемые наборы: ordinary = `integwrapfix/ordinary-expected.txt` (200); cfg-on — новый файл
  `cleanup/cfg-on-expected.txt` = `integwrap/cfg-on-expected.txt` с полной заменой
  `verify::correct::contract_insert_tail_u8_prefix` → `verify::network::contract_insert_tail_u8_prefix` (382);
  исторические файлы не переписывать. Сверить по source.

## Сборки (≤ 2, ≤ $1.4)

G1 inventory controls:false (exact 200 по именам); G2 inventory controls:true (exact 382 по именам; компилирует
cfg-on дерево). Каждый: kind inventory, runner `gcb-e2-standard-4`, `inventory:true`, `harnesses:[]`,
`harness_timeout_minutes` 20; поля kani_jobs/uninit_checks/worker не указывать. Резерв 2×(20+30)×0.0135 = $1.35.
Inventory подтверждает компиляцию и список, не доказательства. PRE-BUILD REVIEW → GO координатора → обе подряд. Library commit отдельно от research, всё
`[skip ci]`, push без force.

## Итог

`RESULT-CLEANUP.md` ≤ 40 строк: library commit/tree, число удалённых строк по файлам, результаты статической
проверки, G1/G2, стоимость. Строка `P1 V5 CANDIDATE library tree <sha>`. Маркеры `REVIEW REQUEST <sha>` /
`CLEANUP ЗАВЕРШЁН`.
