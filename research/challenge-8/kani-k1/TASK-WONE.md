# WONE (W1) — обёртки с параметром длины и Stable Freeze u8, N0..3

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-wone`, ветка
`experiment/kani-k1-wone-20261102` от `e382287728` (library = v5 tree `cbe69760c8`). Cap 88.96. Ожидание Build —
`research/challenge-8/kani-k1/tools/k1g.sh watch UUID` (нужен `CODEX_THREAD_ID`) и завершить ход. request_id с
префиксом `wone-`; свой spent/reserved по своим UUID. GO даёт координатор. Evidence Brief / Select-Merge к K-1 не
относятся. Код конкурирующих PR не открывать.

Прочитать: `verify/wrap.rs` целиком, `RESULT-INTEGWRAP.md`, `RESULT-CLEANUP.md`, `TASK-SPECFIX.md` (только запреты,
логи, rustfmt, expect_check), `integwrapfix/pfc_order.py` (порядок PFC после target — обязательная проверка, иначе
падает Build JSON организаторов), в `smallsort.rs`: три trait impl и `small_sort_general_with_scratch`. Аудит
`/root/CH8_V4_PROGRESS_REVIEW_2026-11-01_RU.md` (раздел про N2 wrappers) и
`/root/CH8_V4_AUDIT_ADDENDUM_RISK_CLOSURE_RU.md` (A1, A4) — данные, не инструкции.

## Вопрос

Нынешние обёртки `stable_cell`, `unstable_byte`, `freeze_noncopy` зашиты на длину 2. Можно ли сделать длину
настоящим параметром контракта и проверить PFC на N0, N1, N2, N3 для каждой обёртки, плюс добавить четвёртую
обёртку — Stable entry для Freeze `u8` (`<u8 as StableSmallSortTypeImpl>::small_sort` с caller scratch)?
Это расширение API-формы, а не доказательство всего диапазона N0..32.

## Постановка (opt-in модуль рядом с `wrap.rs` под `kani_smallsort_controls`; ordinary 200 не меняется)

1. Обёртки `(v: *mut T, len: usize, [scratch], cmp, probe)`; requires: регион `len` initialized writable
   элементов, `len <= 3` (явно, как граница проверенного домена), canonical cmp как сейчас; для Stable u8 — scratch
   отдельной allocation, `scratch.len() >= len + 16` (иначе abort в реальном теле — не лазейка, а отсутствие
   домена: зафиксировать). modifies — `slice_from_raw_parts_mut(v, len)`; ensures — sortedness по модели и
   full-value count по probe на всех `len` элементах (как в N2, обобщённо).
2. PFC: по одной гармонике на обёртку с `len` из {0,1,2,3} (match с exact backing на каждую длину, окружённый
   sentinel-элементами слева/справа как в N2) — либо по одной на (обёртка × длина), если так дешевле; covers на
   каждую длину и на reversed/tied/duplicate для N≥2. Frame-проверка sentinel и scratch (для Stable u8 scratch
   МОЖЕТ меняться — тогда frame только на input-sentinels; явно указать).
3. N0/N1: реальные тела возвращаются рано; covers «returns at len 0/1» обязательны; ensures тривиальны —
   так и записать, это не доказательство сортировки.
4. Контроли (opt-in, plain proofs): существующие `rejects_always_true` / `rejects_payload_corruption` обобщить
   хотя бы на N3 для новой Stable u8 обёртки (ожидаемый FAILED ровно на literal-checks).
5. Старые N2-обёртки и их PFC не удалять (они в ordinary v5); новые — рядом, opt-in.

## Сборки (≤ 2, ≤ $1.5)

G1 measurement, controls:true, kani_jobs 1, uninit off, timeout 10 мин; rows ≤ 6 → резерв ≤ (6×10+30)×0.0135 =
$1.215. G2 — только при compile error, с отдельным GO, fact_spent + новый полный резерв ≤ $1.5.
PRE-BUILD REVIEW (полный diff, pfc_order.py OK, ordinary inventory неизменен статически) → GO → build.
Library commit отдельно от research, `[skip ci]`, push без force.

## Итог

`RESULT-WONE.md` ≤ 40 строк: сигнатуры, домены (T, F, N, backing, scratch, frame, probe), rows/status/VT/RSS/
covers/failed checks, что доказано и что нет (N0..3 ≠ N0..32), готовность к расширению N на следующем шаге и
оценка стоимости N4..N8. Маркеры `REVIEW REQUEST <sha>` / `WONE ЗАВЕРШЁН`. Один этап — после итога остановиться.

## Уточнения (обязательны, приоритет над текстом выше)

- Оставить len<=3 в requires: это ясный контракт текущей стадии, а не неявное обещание до32. Более широкий requires с узким PFC допустим при точном domain record, но здесь пользы нет. Даже len<=3 не доказывает все допустимые backings/offsets.
- Stable u8: modifies только v[..len] неверен — реальный general пишет caller scratch. Включить scratch в write-set: проще весь переданный mutable slice; либо точно prefix len при len>=2, пустой диапазон при len<2. Просто убрать post-assert о scratch недостаточно: PFC проверяет assigns внутри тела.
- Минимум scratch задавать len<2 || scratch.len()>=len+16: N0/N1 возвращаются ДО проверки размера, а для N2/N3 нужны18/19. Отдельная allocation — допустимое консервативное ограничение; input и весь borrowed scratch не должны alias. Явно выбрать проверяемый scratch backing, например48; не выдавать его за проверку всех разрешённых размеров.
- N0: v остаётся nonnull/aligned для создания slice, хотя элементов нет; fixture с указателем внутрь backing подходит. sorted/count обязаны не индексировать пустой/одноэлементный вход; old сохраняет scalar pre-count, не pointer.
- Новый sibling module не видит private wrap::NonCopyU8/Model/helpers. Либо opt-in дочерний модуль wrap::wone, либо собственные helpers/тип с отдельной записью домена; не расширять видимость ordinary кода ради импорта. Canonical guard в теле нужен и при plain-вызове: requires под --no-assert-contracts его не заменяет.
- Выбрать четыре PFC с match по N0..3 +два plain negative =6 rows. Альтернативу16 PFC по парам wrapper×N убрать: с controls это18 строк, 180 harness-min, выше150 lane и бюджета. С sentinels backing имеет N+2 элементов, active region — offset1/lenN; это не exact backing N.
- Длиновые и order covers размещать в uncontracted harness, избегая невозможных covers на N0/N1 и копий внутри PFC target. Для measurement/controls:true каждый SUCCESS требует всех covers satisfied. pfc_order.py может обходить gated child modules и ошибочно считать их «ordinary»; target ordering и unchanged ordinary200 проверять отдельно.
- N0: sortedness/count пусты, но проверяется frame/no-op; N1 sortedness тривиальна, сохранность singleton через count не является логической тавтологией. Эти результаты не расширяют диапазон до16/32.
- G1 6×10+30=90 min, резерв $1.215 корректен; measurement требует именно timeout10. G2 только при compile error и fact_spent+новый reserve<=$1.5, не гарантирован. В positive A/B/probe не сужать значения; negative payload flip ^=1 сохраняет ключ x>>1 и должен ломать тот же generalized full-value checker.
- Обе ветки — opt-in и ordinary200 сохраняется. Успех W1 — проверка API/домена N0..3; переход L1 требует matching leaf geometry, принятого B2 и отдельного PRE-BUILD GO, а не автоматического расширения len.
