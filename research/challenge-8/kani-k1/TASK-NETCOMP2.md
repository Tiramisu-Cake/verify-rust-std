# NETCOMP2 — исправление cover N9 и композиция N13 одним Build

Исполнитель: Codex, свежая clean-room сессия. Worktree `/root/verify-rust-std-kani-netcomp`, ветка
`experiment/kani-k1-netcomp-20261102` @`763b098cd0` (продолжение; старый NETCOMP остановлен, его G2 не возобновляется).
Cap проекта $88.96 (остаток ≈ $11.3); cap этого этапа $1.40, ровно 1 GCB Build, request_id `netcomp2-*`.
Ожидание — `research/challenge-8/kani-k1/tools/k1g.sh watch UUID` с `CODEX_THREAD_ID`, затем завершить ход.
PRE-BUILD GO координатора обязателен. Evidence Brief / Select-Merge к K-1 не относятся. Код конкурентов не открывать.

Прочитать: `TASK-NETCOMP.md` целиком (механизм, домен F=U8Cmp, запреты, размещение, controls, формат RESULT —
действуют и здесь, кроме ступеней/бюджета), `RESULT-NETCOMP.md`, `verify/network/netcomp.rs`.

## Что сделать

1. N9 fix: G1 PARTIAL из-за cover «netcomp N9: all actual exchanges intercepted» в `check_context9`, который в
   общем `run9` достижим только при composed — в A9 он недостижим. Перенести этот cover в
   `netcomp_composed_u8_n9` сразу после `positive9(true)` (как `kani::cover(context9().hits == 25, …)`).
   Больше ничего в N9 не менять.
2. N13: добавить по тому же механизму (без рефакторинга N9 targets/shared assertions) concrete `swap_net13`,
   no-stub leaf13 на exact backing13, Context13/adapter13/bridge, B13 composed (hits 45), wrong-cmp13, count-negative13.
3. Один Build, ровно 7 exact rows: A9, B9, count-negative9, leaf13, B13, wrong-cmp13, count-negative13.
   Резерв (7×10+30)×$0.0135 = $1.350. Measurement, controls:true, jobs1, uninit off, unwind25, 600 s, прежние pool/pin/flags.

## Итог

`RESULT-NETCOMP2.md` ≤ 45 строк, формат как в TASK-NETCOMP; G1 PARTIAL и NETCOMP2 gate разделить.
Маркеры `REVIEW REQUEST <sha>` / `NETCOMP2 ЗАВЕРШЁН`. Один этап — затем стоп.

## Уточнения (обязательны, приоритет над текстом выше)

- Предпочтительнее перенести `kani::cover(context9().hits == 25, "netcomp N9: all actual exchanges intercepted")` из check_context9 в netcomp_composed_u8_n9 сразу после positive9(true). Это сохраняет B9 cover, убирая его из direct proof graph. Все assertions hits/root/pair/frame/canonical/count-invariant оставить на прежних местах; переносить сам check_context9 из общего run9 не следует.
- Удаление optional cover допустимо по смыслу, поскольку hits==25 уже assert и normal-return covers есть, но перенос точнее сохраняет прежний B9 inventory. Не менять validator/порог и не принимать старые4/5 как полный gate. Новые ожидаемые N9 covers: A9 4/4, B9 6/6.
- «Код N9 controls не меняется» верно не для всех зависимостей: count-negative вызывает run9→check_context9. После переноса его общий cover исчезнет, inventory станет3/3 вместо4/4; invariant/hits и intended failed count assertion остаются. Поэтому предлагаю включить этот negative в NETCOMP2. Leaf9 вызывает swap_net9 напрямую, wrong-cmp9 не входит в run9: они от этого исправления не меняются.
- Семь exact rows: A9, B9, count-negative9, no-stub leaf13, B13, wrong-cmp13, count-negative13. Measurement/controls:true/jobs1/uninit off/unwind25/600s и прежний pool/pin/flags. Резерв `(7×10+30)×$0.0135=$1.350`; stage cap явно обновить с$1.215, один Build без повтора, отдельные review/GO/request_id netcomp2-*. Старый NETCOMP остановлен, его G2 этим автоматически не возобновляется.
- Leaf9 7/7 и wrong-cmp9 2/2 можно не повторять при побайтовом сохранении соответствующих targets/roots/annotations и их зависимостей, одинаковых T/F/CMP/probe/backing/frame/pin/flags. В PRE-BUILD приложить сверку зависимостей. Ссылаться на исходный G1 build/source как на переиспользуемое evidence; не представлять их как строки нового Build. N9 count-negative9 будет новым результатом изменённого пути.
- Если принципиально оставить6 строк/$1.215, его старый count-negative допустимо привести лишь как исторический FAILED с4/4 и явной оговоркой об изменившемся cover-site; новый3/3 без запуска не установлен. Предпочтение — семь строк, доплата$0.135 закрывает эту неоднозначность.
- N13 добавлять отдельно, без рефакторинга N9 targets/shared assertions. Самостоятельный no-stub leaf exact backing13 обязателен; leaf9 не переносится на N13. Сохранить explicit U8Cmp/canonical strict_less, independent full inputs/probe, actual raw→adapter13→verified summary, hits45 и весь invariant. Wrong-cmp должен достигнуть того же actual adapter, count-negative — сохранить sortedness после v[12]=1 и упасть только на новом count literal.
- В check_context13 с самого начала оставить assertions; optional complete-hit cover размещать в B13-root, не в helper, который могут компилировать direct/negative roots. До GO перечислить достижимые covers каждой новой строки, а не только aggregate. При добавлении ровно4 N13 harnesses ожидается ordinary200/cfg-on395; это статическая сверка состава, не proof.
- Один общий Build означает совместную подачу, а не гарантированный порядок «сначала принять N9, затем запустить N13». Новый task должен явно разрешить пакетную проверку; конечный gate требует новых A9/B9 с полными covers, сохранённого leaf9/binding evidence, актуального count-negative9, SUCCESS leaf13/B13 и intended failures обоих N13 controls. При неполном gate сохранить per-row facts и остановиться; без условного ретрая/подмены критериев.
- В RESULT разделить G1 PARTIAL и NETCOMP2 gate. Старый38.2% — наблюдение при неуспешном measurement gate. Для новых A9/B9 сравнить текущие VT; `VT(B9_new)+VT(leaf9_old)` отдельно пометить как смешанную оценку из двух запусков, не same-build measurement. CBMC peak max(B,leaf), не сумма; compiler/driver RSS отдельно. Для N13 без matching direct fn-pointer baseline speedup не установлен, даже при успешной композиции.
