# U64-N9 — typed leaf и actual-route композиция Unstable u64 N9

Runtime: **Claude Code**. Исполнитель работает сам, **без субагентов**. Worktree
`/root/verify-rust-std-kani-u64nine`, ветка `experiment/kani-k1-u64nine-20261102`, база
`58d464ce1ce3d3ad7e60325e3297fdf07d38db4c` (NETCOMP2), library commit
`f4d3775dc505ef26e30158cfa7e78f120cd3c30e`, tree `3b6d2a51dae08e52464f4b2b82f5168d8ba9977b`.
Cap проекта$88.96; used/остаток при постановке≈$77.93/$11.03. Cap этой стадии$2.00, один плановый Build,
максимум2 только по compile-error ветке ниже. NET18-LEAVES имеет отдельный cap$1.70 и свои UUID;
его затраты/резерв не присваивать себе. Stable owner/ledger назначает существующий K-1 coordinator,
request_id `u64nine-*`; PRE-BUILD REVIEW и exact-packet GO координатора обязательны.
Ждать через `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD` **в фоновом Bash task Claude Code**;
использовать его завершение/статус, без Codex watch/CODEX_THREAD_ID, polling-субагентов или запуска новых сессий.
Evidence Brief / Select-Merge к K-1 не относятся. Clean room: код/ветки/diff решений конкурентов не открывать.

## Вопрос и решение о стадии

Можно ли повторить механизм NETCOMP2 для T=u64, N9: independently checked real swap summary + raw-call bridge
+ machine-checked whole-network full-value count invariant? Отдельной leaf-only сессии не требуется:
leaf и consumer проверяются одним пакетом; theorem consumer принимается **только вместе с SUCCESS leaf**.

u64 — Copy+Freeze, efficient swap (size8), 8×32≤4096: настоящий Unstable entry выбирает **network**, не general.
При N9: sort9_optimal (25 swap_if_less calls), insertion offset9 без вставок, no merge/scratch transfer.
F явно `type U64Cmp = fn(&u64,&u64)->bool`, value существующего `network::StrictU64::CMP`,
то есть reified `strict_less::<u64>`, ordinary `<`, полные64-битные значения/independent probe.
Это новый typed domain: u8 summaries, LtU64 (`x>>1`) и function-item F не подменяют его.

Прочитать RESULT-NETCOMP2/TASK-NETCOMP2 и запреты TASK-NETCOMP; в netcomp.rs — swap_net9/leaf9,
Context9/bridge/adapter/run9 и три composed roots; в network.rs — StrictU64, strict_less, pure count/sortedness
helpers, существующие u64 swap-profile PFC. В smallsort.rs — dispatch, sort9, raw swap, empty insertion.
TASK-SPECFIX — запреты/format/expect_check/evidence commands; pfc_order.py — target ordering.

## Разделение с параллельным NET18-LEAVES

Выбрать **sibling `network::u64nine`**, файл `verify/network/u64nine.rs`, а не child внутри netcomp.rs.
В `verify/network.rs` только добавить в конце `#[cfg(kani_smallsort_controls)] mod u64nine;`.
NET18-LEAVES добавляет `netcomp::neteighteen` в другой parent — netcomp.rs; так даже регистрации не перекрываются.
Private StrictU64/helpers доступны своему child u64nine без расширения visibility; netcomp.rs читать как образец,
не менять и не импортировать его private u8 targets/context. Не факторизовать общий u8/u64 framework сейчас.

Исходные u8 roots/targets, ordinary cases, runtime smallsort.rs, Cargo/flags/tooling/workflows/pin неизменны.
Не cherry-pick/fetch-integrate NET18/v6/DOMSIX и не править чужой worktree. Source-интеграция веток позже отдельная;
RUN-REQUEST и research records каждой ветки — собственные, не общий живой файл между worktrees.
Ordinary exact200; при ровно4 новых roots cfg-on395→399 статически. Counts не означают formal verification.

## Новый typed summary и независимый leaf

1. Конкретный private target `swap_u64_net9(v:*mut u64,a:usize,b:usize,cmp:U64Cmp,probe:u64)`, до его PFC.
   По образцу u8: requires canonical received cmp; nonnull/aligned full readable initialized/writable region9,
   a,b<9, a!=b, одна allocation и swap geometry. PFC fixture — exact initialized `[u64;9]`, base offset0.
   Modifies только выбранные `v[a]`,`v[b]`. Ensures через StrictU64 pure model: conditional transfer двух полных
   pre-state u64, post-pair ordered, `old(count9_u64(v,probe)) == count9_u64(v,probe)`.
   Old сохраняет scalar count/pair values; не old(pointer) с post-state чтением. Specs callback не вызывают.
   Actual body: `let mut actual:U64Cmp=cmp; swap_if_less(v,a,b,&mut actual)` — никаких summaries/stubs внутри.
2. `u64nine_leaf_u64_n9`: proof_for_contract этого target, unwind25. Все9 входных u64 и independent u64 probe —
   полные kani::any; произвольные distinct in-range a/b, explicit canonical U64Cmp. Никаких stubs/assumes.
   После call explicit pair-transfer/order, typed full-value count и frame остальных7 элементов.
   Семь достижимых covers по u8 leaf: swap/no-swap, first→last, last→first, interior pair, probe hit/miss.
   Существующий swap_profile<StrictU64> PFC полезен как образец, но новый counted target им не доказан.

## Actual call → summary и composed positive

Свой ContextU64Nine: base:*mut u64, probe:u64, initial_count:usize, hits:usize; dedicated static state,
set до library call обычными присваиваниями/вычислениями, без assume. Context не разделять с u8/NET18.
Raw adapter имеет параметры/возврат/two generic T,F как swap_if_less; closed trait impl **только u64/U64Cmp**,
без blanket/fallback. Передать фактические base/a/b/*is_less и выбранный by-value probe в swap_u64_net9;
canonical внутри adapter не подставлять вместо received value.

В adapter до summary assert actual base==registered root, a/b distinct/in-range, received cmp canonical.
Guard literal `u64nine canonical comparator required`; при false вернуть управление без summary call.
Вне PFC target после verified summary увеличить dedicated hits и проверить count9(actual base,ctx.probe)==
ctx.initial_count. Target pair-only modifies не включает context/hit counter; leaf не читает ghost context.
На actual-entry return проверить hits25, base/probe/initial-count frame, canonical cmp unchanged.

`u64nine_composed_u64_n9`: plain proof, `stub(raw swap_if_less, adapter_u64nine)` и
`stub_verified(swap_u64_net9)`, unwind25. Actual `<u64 as UnstableSmallSortTypeImpl>::small_sort`,
полный `[u64;9]=any`, snapshot до сортировки, independent `probe:u64=any`, explicit canonical U64Cmp.
Final assertions sortedness/full-u64 count; реальные network/insertion bodies не заменять.
Четыре обычных covers: sort moves, probe hits, probe misses, duplicates; добавить cover
`probe>u8::MAX as u64 && count(pre,probe)>0` для явной достижимости high-bit значений.
В adapter один reachable entered-cover; complete-hits cover **в composed root** после return. Итого7 required covers.
Общие context/check/run helpers содержат assertions, но не положительные covers с чужой областью достижимости.
Direct A64/bool composed=false ветку не добавлять; speedup здесь не измеряется.

## Два отрицательных контроля

- `u64nine_wrong_cmp_u64_n9`: настоящий entry и те же adapter/stub_verified annotations; valid full geometry,
  register context, но received `cmp:U64Cmp=always_true_u64`. Cover достижения entry и adapter обязательны.
  Не проверять sorted/count результата или hits25 в этом root: expected FAILED только canonical guard literal
  выше (повторения одного guard при25 calls допустимы). Это actual-call binding control, не прямой вызов summary.
- `u64nine_count_negative_u64_n9`: canonical composed path на `[P;9]`, probe=P, где `P=1u64<<40`.
  Все hits/invariant/frame сначала обязаны пройти. После return `v[8]=1u64<<41`: значение больше P,
  порядок остаётся, count(P)9→8, при этом младшие32 бита не меняются. Такой witness проверяет чувствительность
  к полным u64, а не только к байту/младшему слову. Проверить sortedness после порчи; covers возврата до порчи
  и достижения count-check; expected FAILED только `u64nine N9 negative: full-value count preserved`.
  Тот же typed checker, что у positive; narrow witness допустим только здесь. С adapter cover —3 required covers.

Никаких u8/u32 casts/truncation/ограничений диапазона input или probe; count result — usize, payload/probe — u64.
Noncanonical guard в неправильном CMP root должен быть единственной failing property; UB/unwinding/geometry/
frame/hits/unsupported/ERROR/OOM/TIMEOUT не засчитывать intended negative. Оба positives требуют все covers SATISFIED.

## Build, gates, бюджет и stop

G1 — один совместный пакет4 exact rows: leaf, composed, wrong-cmp, count-negative. Measurement/controls:true,
jobs1/uninit off/unwind25/unwinding assertions, timeout10min, k1-standard4/16GiB/swap off, прежние pin/tooling/flags.
Резерв `(4×10+30)×$0.0135=$0.945`. Вместе с плановым NET18 G1 $0.810 —$1.755, но две независимые стадии/ledger owners.
At most2 project queued/running/unresolved Builds, one per stable owner; проверить оба слота и global ledger через
существующий coordinator до GO. Не запускать второй свой Build, пока первый не terminal и корректно учтён.

Gate: identities match; независимый leaf и actual composed SUCCESS с intended checks/7 covers каждый;
wrong-cmp FAILED только canonical literal с2/2 covers; count-negative FAILED только count literal с3/3 covers;
source/runtime/ordinary/tooling restrictions соблюдены. Порядок выполнения rows не обещает ранний stop:
если leaf не прошёл, даже SUCCESS consumer не получает composition credit.
TIMEOUT/OOM/FAILED/coverage/UNKNOWN → сохранить per-row facts, overall PARTIAL/FAIL и остановиться;
не уменьшать width/input/probe, не переходить к N13/18 и не увеличивать timeout/RAM.
G2 разрешён только после compile error G1: тот же вопрос/механизм/domains/4 rows, новый review/GO,
полный reserve$0.945; own fact_spent+reserve≤$2.00 и актуальный общий ledger/слоты соблюдены.
Два полных резерва$1.890≤$2.00; G3 нет. Resource/semantic/coverage repair не разрешён автоматически.

PRE-BUILD: diff, domain T/F/CMP/probe/backing/offset/init/frame; actual25 call-map и stubs/leaf independence;
ctx lifecycle/ghost-write boundary; literals/required covers каждого root; request/source/library/pin/tooling hashes;
ordinary200/cfg399 статически, pfc_order и target ordering отдельно; rustfmt/whitespace; own/global budget и slots.
Library/research commits отдельно, `[skip ci]`, push без force. Код competing branches/чужие live configs не читать.
Компиляция/проверка только в разрешённом GCB; локальные cargo/rustc/Kani/proof и Actions dispatch запрещены.
Evidence — bounded K-1 summaries/rows/peaks/разрешённые targeted excerpts. Raw archives/full logs/Cloud Logging,
credentials/скрытые configs не читать/скачивать; historical evidence/ledger не переписывать.

## Итог

`RESULT-U64-N9.md` ≤35 строк: reviewed/build/library/request identities; actual T/F/CMP/domain и raw→adapter→
summary/leaf связь; rows/status/VT/CBMC RSS/failed-total/unreachable/covers и gate; own spent/reserved.
VT не напечатан → UNKNOWN, timeout cap600 не выдавать за завершённый VT; OOM отдельно.
Показать compiler/driver/process-sum RSS отдельно от CBMC. B+leaf VT можно дать как цену доказательства,
но без matching A64 нет speedup; сравнение с u8 — только разные typed experiments, не универсальное масштабирование.
При gate PASS установлен exact u64/U64Cmp/default-< N9 theorem на backing9/offset0 с independent full-u64 probe,
matching real leaf/pair-frame-count invariant; это opt-in research. Не установлены function-item F, arbitrary T/FnMut,
N13/18/32/другие backings/offsets, stability ties, uninit detection/full alias-validity/unwind scope или trait PFC.
Ни ordinary200 этой ветки, ни зелёный Part1-v6/202 автоматически не расширяются.
Маркеры `REVIEW REQUEST <sha>` / `U64-N9 ЗАВЕРШЁН`; один stage — после результата стоп.

## Уточнение координатора

Stable owner этой стадии — `"agent": "k1-merge"` (NET18-LEAVES идёт под `k1-network`). Слот и ledger — по k1-merge.
