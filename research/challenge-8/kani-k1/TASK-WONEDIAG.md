# WONEDIAG — диагностика стоимости трёх обёрток W1 на фиксированном N3

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-wonediag`, ветка
`experiment/kani-k1-wonediag-20261102` от W1 `1c107cb12a`. Cap 88.96. Ожидание Build —
`research/challenge-8/kani-k1/tools/k1g.sh watch UUID` (нужен `CODEX_THREAD_ID`) и завершить ход. request_id с
префиксом `wonediag-`; свой spent/reserved по своим UUID. GO даёт координатор. Evidence Brief / Select-Merge к K-1
не относятся. Код конкурирующих PR не открывать.

Прочитать: `RESULT-WONE.md`, `TASK-WONE.md` (раздел «Уточнения»), `verify/wrap.rs` (модуль `wone` и старые N2
обёртки), `TASK-SPECFIX.md` (только запреты, логи, rustfmt, expect_check), `integwrapfix/pfc_order.py`.

## Вопрос

В W1 три PFC на N0..3 не уложились в ресурсы: `unstable_byte` TIMEOUT (2.1 GB), `freeze_noncopy` TIMEOUT
(15.6 GB), `stable_byte` OOM (15.7 GB). Гипотеза (не установленная причина): совместный вклад match/union по
четырём длинам, четырёх backing N+2 и длинозависимых pointer/model/frame выражений. Становятся ли эти три PFC
дешёвыми на одной фиксированной длине N3?

## Постановка (opt-in, рядом с `wrap::wone`; ordinary 200 не меняется)

1. Три новые PFC — только для трёх неуспешных обёрток (`unstable_byte`, `freeze_noncopy`, `stable_byte`); Stable
   Cell не повторять. Фиксированный N3: backing5, active offset1, len — литерал 3, без старого match/len-dispatch.
2. Сохранить прежние unrestricted A/B/C/probe/sentinels; не сортировать вход заранее, не связывать probe с
   элементом, не убирать asserts/frame/covers. Stable u8 — caller scratch48 отдельной allocation, как в W1.
3. Target-функции, canonical fn-pointer F, requires/ensures/modifies и реальные тела не менять.
4. Covers: заменить агрегированные covers по длине на N3 return/reversed/tied/duplicate/hit/miss там, где они уже
   требовались; невозможные для N0/N1 covers не переносить. SUCCESS строки = intended checks + все её covers.
5. Negative controls не повторять (старые не изменились; их прошлый успех не заменяет новые PFC).

Не входит в этот этап (только оценка в RESULT): пара «fixed-N3 contract vs plain real-entry N3», вариант Stable u8
с modifies prefix3 вместо whole-slice (allocation scratch48 сохранить, frame enforcement включён), N2/N4+.

## Сборка (1, резерв $0.810)

G1 measurement, controls:true, kani_jobs 1, uninit off, timeout 10 мин, 3 rows → (3×10+30)×0.0135 = $0.810.
Один Build без автоматического повтора; G2 нет. PRE-BUILD REVIEW (полный diff, pfc_order OK, target ordering и
ordinary 200 проверены отдельно) → GO → build. Library commit отдельно от research, `[skip ci]`, push без force.

## Итог

`RESULT-WONEDIAG.md` ≤ 35 строк: rows/status/VT/RSS/covers/failed checks; сравнение с W1 N0..3 по каждой обёртке.
Выводы осторожно: если N3 резко дешевле — это поддерживает влияние union/match/backings вместе, но не разделяет их;
если по-прежнему дорого — их вклад не исключён. Доказано только N3 в этих fixtures, не N0..3 и не N16. TIMEOUT/OOM
— resource outcomes, не vacuous/ошибочный контракт/FAILED. Если Kani не напечатал Verification Time — VT=UNKNOWN.
Предложить следующий точечный шаг (одна пара, не матрица). Маркеры `REVIEW REQUEST <sha>` / `WONEDIAG ЗАВЕРШЁН`.
Один этап — после итога остановиться.

## Уточнения (обязательны, приоритет над текстом выше)

- WONEDIAG: новые PFC разместить внутри существующего wrap::wone либо в его opt-in дочернем модуле после targets. Соседний модуль не видит private *_len/helpers. Не расширять visibility и не копировать NonCopyU8/comparators/targets: нужны прежние Rust T/F/CMP и те же контрактные функции.
- WONEDIAG: создать отдельные uncontracted N3 covers; input_covers(3, ...) использовать нельзя — там останутся недостижимые N0/N1/N2 covers. Сохранить N3 return, reversed, increasing, tied-distinct, duplicate, independent-probe hit/miss (7 достижимых covers), а также прежний input_frame после возврата. Явно построить backing5 и передать literal3; не вызывать with_backing!(3, ...), сохраняющий исходный match в раскрытии макроса.
- WONEDIAG: Stable u8 передавать весь прежний отдельный uninitialized scratch48 и оставить whole-slice modifies; не заимствовать только prefix19/3 и не инициализировать scratch ради ускорения. Это изменило бы дополнительный фактор. Для первого сравнения сохранить unwind16 и все проверки исходных PFC; иной bound требует обоснования до GO.
- Оба задания: старые harnesses оставить без изменений, в request выбрать полные exact имена только новых строк (3 WONEDIAG / 2 NETTHIRTEEN). Не запускать весь controls-набор с унаследованными TIMEOUT/OOM/expected failures. Статически ожидать ordinary200 и cfg-on391 для WONEDIAG, ordinary200 и cfg-on386 для NETTHIRTEEN; эти counts подтверждают состав, не proofs. Не переносить ветки на MACSPLIT/v6 в рамках пилотов.
