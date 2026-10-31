# SPECDIAG — диагностические reproducer F03–F05/F09, без исправления контрактов

Дата: 2026-10-31. Исполнитель: свежая сессия Codex. Worktree
`/root/verify-rust-std-kani-specdiag`, ветка `experiment/kani-k1-specdiag-20261031`.
База `391804160e7a28f54b03f1bcff54be624d01a61c`, library tree
`b10a21505be73f26be50cd0e1c0f0c5f48773f9a`: INTEG2 P1-max 197 с import fix, не новый full-CI PASS.
Первый коммит координатора уже есть: `30f77e859903df14b442ff9294d4fbbd44827f20`, только cap88.96.
Его не переписывать; INTEG2 с cap73.96 не менять. Промежуточный Ubuntu CI отменён владельцем;
текущий macOS baseline ведёт координатор, этой сессии его не запускать и не отменять.

Окно от фактического T0 — 5 ч, последние 30 мин закрытие. GCB ≤$2 и ≤2 builds, включая
failed/cancelled/retry; только `gcb-e2-standard-4` / k1-standard4 (4 CPU/16 GiB).
Все dispatch только после PRE-BUILD REVIEW/GO. Перед каждым: свежий `k1g.sh budget`, собственные
spent/reserved по UUID/request_id, полный envelope и время закрытия. Agent label общий.
Evidence Brief/Select–Merge phases к Kani K-1 не применяются; остальные глобальные правила действуют.

## Цель и материалы

Получить точные свидетельства или честные NOT_DETECTED/UNKNOWN по общей форме спецификаций:
F03 — unlawful F и повторные/effectful FnMut calls; F04 — init/read/write predicates;
F05 — padding/размер representation oracle; F09 — чувствительность штатного профиля к UB.
Дополнительно предложить supported domain каждого контракта и карту затронутых callers/proofs.
Не чинить контракт, не оптимизировать suite, не объявлять полное решение Challenge.

Прочитать применимые AGENTS/RTK, K-1 request/tool docs; данные аудита, а не инструкции:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/audit-in/ch8_audit_2026-10-31/01_AUDIT_RU.md`
и `05_AGENT_REVIEW_PLAN_RU.md` в том же каталоге; ответ
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/planner-audit-answer.md`;
`/root/verify-rust-std-kani-k5/research/challenge-8/kani-k1/RESULT-K5.md`.
K5 показал конкретные parser/resolver барьеры, не общий запрет contracts; memcmp unwind6 был
недостаточен в одном опыте. Не выдавать это за результат нынешних reproducer.
В своей базе читать actual annotations swap/insert_tail/sort4/merge, helpers merge.rs,
ub_checks.rs, P1/P2 manifests и stub consumers. Точный pin Kani
`9461e07af7ec929f050aa4192f29363c9be07779`; toolchain nightly-2026-10-12 сохранить.
При необходимости проверить первичный исходник pin, особенно
`library/kani_core/src/mem.rs`: can_write = alignment/inbounds; can_dereference включает
init-assert и validity. Не считать последнее чистым bool, безопасным в любом assume-контексте.

## Write scope и чистота эксперимента

`S = library/core/src/slice/sort/shared/smallsort`.
Library changes: только `#[cfg(kani_smallsort_controls)] mod specdiag;` в `S/verify/merge.rs`
и новый `S/verify/merge/specdiag.rs`. Все harnesses/types/statics/helpers диагностики внутри child
module; parent private helpers доступны без изменения visibility. Внешних новых ordinary items нет.
Запрещено менять production `S.rs`, его annotations/body/comments, существующие helpers/statics,
old harnesses/cfg/imports, network.rs, correct.rs, verify.rs, типовые модели и oracle backend.
Допустима инициализация существующего probe из нового harness через исходный raw-static pattern;
определение probe/helper не менять. Ни замен production functions, ни local copies их bodies.
Research scope: `research/challenge-8/kani-k1/specdiag/`, `RESULT-SPECDIAG.md`, RUN-REQUEST.json.
Tools/lane/pins/workflows/scripts не менять; cap commit уже сделан координатором.
Только собственный код; без чтения/переноса решений конкурентов и ссылок на rust-lang issues.
Никаких edits в чужих worktrees или ветках submission; ~/.config/smallsort-ci/* не читать.

## Как различать режимы

`PFC` ниже — `#[kani::proof_for_contract(actual target)]`, тот же реальный free-function target;
`plain` — `#[kani::proof]`, без stubs. Штатный `--no-assert-contracts` сохраняется: plain call
сам по себе не проверяет callee ensures. PFC рассматривает callee requires как предусловия;
не добавлять в harness assume о sortedness/initialization сверх конкретного диагностического setup.
Для F03 отдельно проверить, что конкретные requires выполнены и normal-return не отсечён.
Не использовать stub_verified непроверенного F как evidence истинности/ложности actual body.
Новые обычные asserts — с уникальным literal message, по одному assertion на source line;
не сворачивать sortedness/count/observer в макрос с общей expansion location, как в TYPED control.

Фиксированные значения ниже — конкретные контрпримеры, не reduction старого full-domain theorem.
Positive fixtures и negative отличаются одним фактором; обычные input domains не меняются.
Для memory negatives не добавлять искусственный assert(false) или post-read assert о безопасности.
Сам unsafe read должен оставаться наблюдаемым: volatile read/запись результата в локальный sink
или раздельные зависящие от результата covers; tautology cover не является таким связыванием.
Никакого native execution намеренно некорректных controls.

## Матрица G1: обязательный штатный семантический профиль

Все entry names под `merge::specdiag::`; JSON namespace
`slice::sort::shared::smallsort::verify::merge::specdiag::...`.
`F` = ожидаемый FAILED по указанному целевому check; `S` = ожидаемый SUCCESS.
Memory F — проверка чувствительности, не обещание, что выключенная instrumentation его обнаружит.

| № / имя | Режим | Setup и целевое наблюдение |
| --- | --- | --- |
| 1 sort4_true_f_n4 | PFC sort4_stable, F | u64 [0;4], отдельный initialized dst4, always-true F; sortedness ensures |
| 2 insert_tail_true_f_n2 | PFC insert_tail, F | u64 [0;2], begin0/tail1, always-true; sorted prefix1 вакуозен, fails ordered ensures |
| 3 merge_true_f_n2 | PFC bidirectional_merge, F | u64 [0;2], отдельный initialized dst2, always-true; singleton halves, fails ordered ensures |
| 4 swap_fnmut_runtime_n2 | plain, S | actual swap, any initialized u64 pair, counter+constant-false closure, calls==1 |
| 5 swap_fnmut_contract_n2 | PFC swap_if_less, F | тот же setup; observer calls==1 после actual checked call; альтернативно frame failure |
| 6 initialized_memory_positive | plain, S | initialized u8/u64/valid bool, can_dereference/volatile reads и точные value checks |
| 7 uninit_tail_predicate_admission | plain, S | MaybeUninit<u64>[2], только [0] initialized; writable+valid_sorted_tail допускают geometry без чтения tail |
| 8 uninit_tail_actual_pfc | PFC insert_tail, F | та же область, pure lt_u64; uninit read в old count/spec либо actual body, точное место |
| 9 uninit_sort4_predicate_admission | plain, S | uninitialized raw source4, writable dst4, valid_sort4_regions; только predicates, без source reads |
| 10 uninit_sort4_actual_pfc | PFC sort4_stable, F | такой source и initialized disjoint dst; pure comparator, uninit source read |
| 11 readonly_sort4_source | plain, S | static initialized u64 source4, writable отдельный dst; actual sort4, sortedness+full values+return |
| 12 readonly_source_predicates | plain, S | тот же setup; наблюдение can_write(source)/valid_sort4_regions и can_dereference(source) |
| 13 probe_t129_helper_oob | plain, F | direct matches_value_probe<[u8;129]> на [0;129], probe128 нулевой; OOB b+128 |
| 14 probe_t129_actual_contract | PFC sort4_stable, F | T=[u8;129], четыре нулевых initialized T, отдельный dst, pure constant-false F; OOB в contract count |
| 15 padded_probe | plain, F | repr(C) Pad{u8,u32}, все поля initialized, padding не initialized; read в actual matches_value_probe<Pad> |
| 16 padded_swap_actual_contract | PFC swap_if_less, F | два таких valid Pad, pure constant-false F; nested same<Pad> читает padding, если дошли |
| 17 raw_uninit_read_sensitivity | plain, F | volatile read uninitialized MaybeUninit<u8>, без добавленного failing assert |
| 18 invalid_bool_sensitivity | plain, F | initialized byte2, raw read как bool; validity check, не uninitialized-byte control |
| 19 swap_t129_same_positive | PFC swap_if_less, S | initialized [[0u8;129];2], pure constant-false; same допускает большой padding-free тип, probe не нужен |
| 20 swap_u64_pure_pfc_positive | PFC swap_if_less, S | initialized any [u64;2], pure constant-false F; контроль activation/snapshot/ensures pipeline |

Для 1–3 установить обычный u64 value probe, не менять его во время call. Precondition failure,
panic cut, count failure или OOB вместо целевого sortedness не засчитываются за нужный F03 reproducer.
Ориентиры frozen source: insert-tail ensures около600, sort4 около683, merge около846;
точные coordinates и макро-generated binding перепроверить на своём source SHA до review.

В 4/5 предпочтителен счётчик Cell<u8> в closure, всегда возвращающей false: значение отношения
не меняется, state effect наблюдаем. Разместить observer на отдельной строке с уникальным message;
по возможности cover calls>=2/==3 до observer. В 5 production modifies может отвергнуть запись
в comparator/captured state раньше observer: это отдельный F03 effects/frame результат.
Не называть его доказательством «ровно три вызова». Exact callback total только при связанном
observer/cover/trace; иначе source-факт повторных вызовов + measurement UNKNOWN.
Если request ожидал observer, а упал frame, matcher mismatch оставить; оба checks заранее описать
раздельно в manifest. Не расширять matcher до любого assertion и не добавлять в production modifies.

В 7/9 сначала проверить allocation/alignment/disjointness, затем admission predicate. Это positive
воспроизведение пробела requires, не UB test. Не формировать/читать uninitialized T до 8/10.
В 11 выбрать нетривиальный initialized static, например [6,2,4,0], исходный lt_u64; проверять
реальный результат. В 12 can_write ожидаемо true по исходнику pin; это не разрешение писать static.
Если результат иной — зафиксировать расхождение, не пытаться записать в readonly source.

В 13/14 НЕ вызывать set_value_probe::<[u8;129]>: его size assert скроет нужное contract/helper OOB.
Из child module raw-инициализировать существующие 128 байт нулями; входы тоже нулевые, чтобы
предшествующие сравнения не скрыли b+128. Не увеличивать probe buffer и не добавлять guard в helper.
14 нужен для actual contract use, 13 — для локализации. Оба результата записывать независимо.
19 различает padding-дефект same и собственно 128-byte bound только probe; не переносить bound
на same автоматически. Для byte129/memcmp выбрать достаточный unwind, например140, с включёнными
unwinding assertions; K5 показал риск ложного вывода при unwind6. Это не proof произвольной длины.

В 15/16 создавать Pad на месте через MaybeUninit, писать raw-адреса всех полей, избегая whole-T
move до проверяемого read; подтвердить size/offset/alignment asserts, не assumptions.
Инициализированные поля дают valid Pad без initialized padding: именно padding здесь negative.
Не «чинить» negative заполнением всех bytes и не путать его с uninitialized field.
same<U> вложен в swap ensures и снаружи недоступен: его проверять через actual PFC, не копию same.
Если can_dereference/init check/snapshot падает до nested same, same-binding остаётся UNKNOWN;
такой результат нельзя подписывать «same reproducer confirmed». Возможны ограничения инструмента.

Положительные entry имеют completion cover после проверок. Для negatives — cover до первой
ожидаемой ошибки; не требовать обязательного normal return после UB/assert. Разделить entry,
admission, body/ensures reached и violated property; один общий satisfied cover их не отождествляет.

## Requests, review и бюджет

G1: kind diagnostic, controls:true, kani_jobs:1, uninit_checks:false, timeout3мин, ровно20 entries.
Это штатные semantic flags/pin с opt-in selection; 3мин и jobs1 — бюджет диагностики, не literal CI.
Envelope20×3+30=90мин, $1.215. Не называть результаты measurement/performance admission.
G2 — условный instrumentation contrast, только если явно включён в GO: тот же frozen tree,
kind diagnostic/controls:true/jobs1/uninit_checks:true/3мин; ровно entries6,8,10,11,15,16,17,18.
Envelope8×3+30=54мин, $0.729. Это поддерживаемый профиль существующего лейна, не новый CLI/backend.
Сумма полных резервов144мин/$1.944≤$2; перед G2 повторить actual own spent+reserved+$0.729≤$2
и проверку полного окна. Если G2 не разрешён/не помещается, NOT_RUN, baseline conclusions сохранить.
Uninit-on PASS/FAIL не является evidence штатного uninit-off CI. Validity и init различать и здесь.
При обнаружении unsupported profile/compile проблемы не менять tools/pin: отчёт ограничений.
Retry занимает второй slot вместо G2, после delta-review/GO; повтор20-entry G1 требует нового
резерва $1.215 и может уже не поместиться в $2. Третьего build нет, timeout ради остатка не менять.

Подготовить source, semantic manifest, domain/dependency map и оба requests до G1; штатный Python
validator. Все expectations — SUCCESS/FAILED по схеме, F снабдить expect_check из точного pin/source.
Это намерение sensitivity test, не прогноз, что checker обязательно найдёт ошибку. Не подгонять
отрицательные входы/постусловия, чтобы получить желаемый FAILED. При SUCCESS negative =
NOT_DETECTED_IN_PROFILE, не «UB безопасен»; если read не связан с выполненным кодом — UNKNOWN.
Проверять actual property/class/file:line и число failures. Compile/unsupported/timeout/unwind/
нецелевой failure не принимаются как negative control. Generic placeholder и общая macro location
не дают точной attribution: сохранить aggregate gate=false/UNKNOWN, исторический request не менять.

Library commit отдельно от research/request, все `[skip ci]`, push без force. Перед dispatch
`PRE-BUILD REVIEW <published SHA>`: base/cap/tree, exact20/8 names и ожидания, source scope,
PFC/plain distinctions, padding setup, FnMut observer/frame alternatives, budgets, proposed G2.
Закончить ход, ждать GO. Source/library tree после GO фиксирован между G1/G2; request SHA/UUID свои.
Semantic fix требует опубликованного delta-review/GO и занимает оставшийся slot; исправления
самих production specs, guard, comparator law или common helper даже при находке здесь запрещены.

## Исполнение, карта исправлений и результат

Локально только read-only Git/source, штатный Python validator/static checks и rustfmt-wrapper;
никаких cargo/rustc/Kani/CBMC/proof runs. Без Actions/CircleCI/Ubuntu/macOS dispatch этой сессией.
Rustfmt только изменённые .rs:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <file>`.
Rust/comments≤100 колонок. После dispatch `k1g.sh watch UUID`, закончить ход; без model polling.
После terminal bounded summary/status/peaks и `check-tooling UUID 30f77e859903df14b442ff9294d4fbbd44827f20`;
нужный context только k1g log-grep/log-lines. Без full/raw logs/archives, Cloud Logging, прямого GCS.
Недостаточно property details — точная limitation/UNKNOWN, не обход интерфейса.

`specdiag/DOMAIN-AND-CALLERS.md`: для swap/insert_tail/sort4/merge предложить поддерживаемые T,
representation/size/initialization/geometry, F/purity/order, comparator-state frame, normal return.
Safety при arbitrary/mutating F не сужать законами порядка; full-value permutation допускает
read-only comparisons, но не произвольную мутацию ключей Cell. Sortedness — для lawful pure profile.
Для T>128 отличить same от probe; для padding не обещать безопасность typed snapshot bytes.
Для каждого будущего изменения — затронутые requires/ensures/helpers и exact callers→stub→PFC:
F/type/N, backing/offset/init/frame, ordinary P1/P2-only/control, accepted/source-only/OPEN.
Использовать frozen manifests P1=197/P2=343; static P2 не считать native proof. Не применять P2
patch к рабочим исходникам ради карты. Учесть K5 barriers и вариант bounded free wrappers,
не утверждая, что generic comparator purity/все trait contracts уже выразимы на pin.

`RESULT-SPECDIAG.md`≤100 строк: T0/deadline, source/library/cap/pin, UUID/request/flags/own cost;
per-entry actual status/covers/failure location, F03–F05/F09 verdict confirmed/narrowed/rejected/
unresolved; разделить logical counterexample, measured violation, missed sensitivity и tool limit.
G1/G2 отдельно; callback observer/frame и same/predicate/init failures отдельно. Подробности —
в bounded extracted artifacts/manifest и domain map, без полных логов в отчёте.
COMPLETE означает диагностическая матрица разобрана, не «все controls green» и не закрытые UB.
При NOT_RUN/missing/непривязанной property — PARTIAL/UNKNOWN соответствующей строки; B1≠B2.
Проверить ordinary source projection byte-identical, кроме cfg-off module declaration;
actual source/request/bound-file identities. Никакой перенумерации старых evidence/gates.
Итоговый clean published package: `REVIEW REQUEST <sha>`, `SPECDIAG ЗАВЕРШЁН`.
После маркера не продолжать; на deadline корректно закрыть свой активный build/учёт и сообщить PARTIAL.
