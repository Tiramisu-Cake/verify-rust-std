# M9 — PRE-BUILD REVIEW

Состояние: кандидат опубликован для GO; dispatch ещё не выполнялся.
Ветка: `experiment/kani-k1-mnine-20261031`.
Исходный commit: `97fdf0a21e517fc99ab0a5180bfb7ee3128685c9`.
Library commit: `b2930031d889065e89054efea16f9a10a409b048`.
Замороженный library tree: `3c5fd2134ca7ed558976b53e1216eeedd0d6b491`.
Подготовка: 2026-10-31 07:35:26 UTC (10:35:26 MSK).

Изменён только `library/core/src/slice/sort/shared/smallsort/verify/merge.rs`:
два прежних guard расширены до 6..=9, два новых private opt-in helper-а scratch,
пять opt-in harnesses: G9, stable N9 aggregate/non-const/const и stable N8 const.
Ordinary harnesses не добавлены; условный stubbed C N9 сохранён.
`source-audit.py` / `source-audit.json`: PASS; прежние items точны кроме guard.
Новые stable helper-ы равны aggregate body кроме имени, allocation и borrow.
Adapter/oracle/lt_u64/probe равны ASSEMBLY library `d4e5a0907b`.
Unwind34, arbitrary input/probe, snapshot, один cover после assert сохранены;
новых stubs, selector, импортов нет. Статический cfg forecast: ordinary+0, controls+5.
Это source audit, не measurement controls и не compiler inventory.

Заданный rustfmt wrapper/config --check: exit0; Rust-строки ≤100.
git diff --check: PASS. Lane-файлы, Kani pin, toolchain, flags не менялись.
Локальные rustc/cargo/Kani/CBMC не запускались; compiler warnings ещё не проверены.
RUN-REQUEST.json валиден: measurement, jobs1, controls:true, timeout10min,
пять точных имён, expected SUCCESS; request_id `m9-g1-measurement-20261031`.

Бюджет подготовки (`k1g.sh budget`): builds114, used$62.1240,
reserved$0.0000, CAP_USD73.96; свободно$11.8360. Это не dispatch preflight.
Личный лимит M9: $2.30 / 2 builds; пока потрачено$0, builds0.
G1 envelope: 5×10min +30min setup =80min, резерв$1.0800.
G2 условный: 4×10min +30min setup =70min, резерв$0.9450.
Итого максимум$2.0250 ≤$2.30. Окно4h, резерв закрытия30min;
оба полных envelope150min + закрытие30min укладываются в окно.
Перед каждым dispatch повторить budget, записать T0/deadline/остаток окна;
T0 и фактические UUID/request SHA пока не назначены, GO ещё не получен.
Не открывать окно сборки без полного envelope и резерва закрытия.

После GO на опубликованный SHA:
1. Проверить чистое дерево, library tree, точный request и lane equality.
2. Записать T0, deadline4h, work cutoff3.5h и dispatch preflight в `m9/`.
3. `k1g.sh budget`, затем dispatch текущей ветки; сохранить UUID/request_id/SHA.
4. `k1g.sh watch BUILD`; завершить ход. Никаких активных ожиданий.
5. После пробуждения: summary и 5 rows, peaks CBMC/driver, check-tooling
   относительно исходного commit; bounded log-grep/log-lines для warnings/covers.
6. Решать по строкам: G2 только при SUCCESS G9 и хотя бы одной S9, с covers.
   TIMEOUT иной формы может сделать aggregate gate false; это неполная триада.
7. Если разрешён G2: diagnostic/jobs3/controls:true, G9, лучшая S9,
   ordinary general_direct_u64_n8 и stable_direct_u64_n8; library tree прежний.
   Повторить budget/preflight, отдельный request commit+push, dispatch+watch+конец хода.
8. Проверить реальное перекрытие ≥3 CBMC, OOM/missing и стоимость своих UUID.
9. RESULT-M9.md по заданию (≤100 строк), отдельный research commit+push;
   итоговые REVIEW REQUEST и M9 ЗАВЕРШЁН только после завершения задания.

N8 исторические опоры BACKING source740d22674c/build
b07fdcd8-fbd8-401e-9948-9e5f9e7201ad: non-const292.468s/7.928GiB,
aggregate214.316s/1.508GiB. Это не matched измерения нового SHA.
Выводы N8 и N9 разделять; fixture48 ≠ любой backing; macOS UNKNOWN;
пригодность подтверждает только CI организаторов. Одну ветвь вместо обеих
для замены C N9 не предлагать; ordinary изменяет координатор.
