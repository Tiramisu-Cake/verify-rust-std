# OVERNIGHT-MERGE-26.10 — CONTINUATION IN PROGRESS

Владелец возобновил работу 2026-10-08; hosted-запуски разрешены до
**14:30 МСК (11:30 UTC)**. Продолжение израсходовало **598/7200 job seconds**
(204 + 209 + 55 + 130), осталось **6602/7200**. Ночная история **3971/21600** отдельно;
старый бюджет **603/1800 (остаток 1197)** также отдельно и не прибавляется.
Ветка `overnight/merge-26.10`; последний proof source / Actions SHA
`8ecc949df41c72c1c2a12371b486e97363a21a93`.
[Фаза/дизайн/матрица](merge/OVERNIGHT-26.10-PHASE.md).
Последний [run 37746828112](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37746828112),
job113210194939, 07:59:02–08:02:31 UTC, **209 seconds**; остальные jobs
skipped. Артефакты полностью проверены. До него:
[37744660894](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37744660894),
proof `6ba53993ffc740a27ddb8bdcf6b9bf2c57bb9f34`, job113203193351,
204 seconds. Активного run нет.
Новый run37748834934/proof2960c082 остановился на git apply stdspec patch
до сборки/матрицы; job11321676197708:17:18–08:18:13UTC55seconds.
Setup failure; контекст и predicted staged hash исправлены, новая матрица pending.

Actual `merge_up` и `merge_down`: exact source/export/decode/refinement,
полные normal/unwind body/return/leak/dead/source gates PASS;
повторены в b04:116/120 execution records,3return+3leak каждый.
Первый proof `5bbd2ef2613106fdc38bd8aeea930cf344390275` /
[37711781188](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37711781188).
Условный домен: positive stride, различные source cells, явный C1 pointer
и отделённый writable destination-option. Arbitrary lawful FnMut effects/answers;
normal сохраняет current source T.own/F.own, копирует выбранное current значение
и двигает cursors; callback unwind сохраняет destination option и возвращает
current source/F ownership. Нет entry snapshot, duplicate T.own или SWO.
Общий generic Challenge НЕ ДОКАЗАН.

G2/A/B, native C/C++, ordinary normal/unwind, старые Rust controls,
W1 22positive+5negative/9bridges и C1 5positive+2stock+6negative PASS.
W1/C1 — TRUSTED bounded primitive summaries. Symbolic zero size wrapping PASS;
4concrete ZST layout цели OPEN,2reentry PASS. Two-hole owned-array3positive+
2intended negatives+mutants PASS. В b04 C1 arbitrary-index geometry5checked
bodies PASS; source/caller/resource связь отдельно OPEN. Scratch3positive
full PASS;3negative+mutants fullPASS в6ba; исходныеb04классификации
INCONCLUSIVE сохранены. C1geometry2negative+mutants fullPASS в6ba.

M2 shape valid+6admission negatives PASS; tuple resource positive+4proof negatives
PASS. HRTB11/11 ADMISSION_CERTIFICATE+fail-closed controls PASS, underlying
11proof statuses INCONCLUSIVE: сертификат допуска не является доказательством.
Cleanup12cases (2positive/frame,6proof negatives,4frontend admission)+mutants PASS.
Полная приёмка объединённого семантического профиля остаётся OPEN;
cleanup patch94fe2cd6 меняет kernel100eebae/translator0e450267.
Console cache exact-hit PASS and all9 cache self-tests PASS; full matrix ran on
console `3a08722c…d68b70f1a`, profile `aeca556c…1906e6`, producer b04.

В run 377468: `merge_up/down` вновь прошли полные normal/unwind/source/refinement
gates (116/120 executions, по 3 return и leak checks); cleanup 12/12,
M2-shape 6/6 admission controls и M2-resource 5/5, owned-array 5/5,
pointer-domain 3/3, scratch 6/6. Trace entry: generic/u32 positive controls
PASS, false assertion достигнута, но осталась INCONCLUSIVE без калиброванного
oracle; nested tuple return probe остановился до входа в тело. G2 trace main
остаётся INCONCLUSIVE: 13 helper bodies PASS, main 0 executions и dead-code.
Actual `bidirectional_merge` выполнил 47 statements и остановился на loop leak
compiler-generated Range/tuple stack chunks; полный proof не получен.
Итог job `success` означает успешный сбор diagnostic matrix, не theorem.

Раздельные открытые блокеры/приоритеты:
A. Full G2 pointer trace: selectors parse FIXED,13helperbodies PASS; main
целиком deadcode/0exec. Exact-domain generic и `u32` entry controls PASS;
false-assertion target достигнут, но остаётся INCONCLUSIVE без oracle. Nested
tuple return probe остановился до body на ownership admission; это не диагноз main.
B. Actual bidirectional len2: `dst_base` scope FIXED, `bidirectional_merge`
исполняет 47 statements; первый failure line387 — 14 leaked field/padding
chunks в четырёх compiler-generated locals: два nested tuple3 и две `Range`
структуры. Actual `merge_up/down` bodies проходят; panic helper body не входит.
Iterator linkage, odd branch, terminal wrapping и panic-frame composition OPEN;
len2 остаётся diagnostic, без full proof.
C. Caller C1 derivation, M2/cleanup full admission, resource composition и
Freeze/shared-slice bridge OPEN; slice.share не создаёт T.own.
D. Functional actual G2/A/B composition OPEN; SWO/immutable keys/faithful answers
будут отдельными функциональными предпосылками.

Следующий подготовленный hosted matrix добавляет отдельный TRUSTED
`usize::is_multiple_of` std-spec summary (patch `0d95bc58…e533d92`, staged
post-stdlib SHA `d5807998…7076e94`) с exact source/alpha-renaming certificate и
6 fail-closed controls; false-result targets должны быть observed, без guessed
oracle. Рядом остаётся exact-domain unsafe nested-tuple constructor для 12 trace
coordinates, чтобы отделить return representation от loop proof. Все старые
матрицы обязательны; stack-address patch в этот запуск не включён. До запуска
осталось 6602 continuation job seconds. Подробный гипотетический исход и
переходы записаны ниже в EXPERIMENT-LOG. Runtime std не меняется. Исторические
результаты сохраняются под их исходными proof SHA.

---

# Challenge 8: upstream synchronization checkpoint

## Переходный checkpoint — Git sync, повторная приёмка НЕ ВЫПОЛНЕНА

2026-10-08. В этой ветке напрямую влит закреплённый upstream cd371e03.
[UPSTREAM-SYNC](UPSTREAM-SYNC.md) фиксирует parents/SHA, исходниковые изменения,
бюджеты и два следующих задания. CI budget этой фазы0; исследования отложены.
Старые принятые результаты ниже относятся только к прежним proof SHA/tool profiles.
Новым std/nightly/VF необходима повторная проверка. S7c UNACCEPTED (пять admission
контролей незавершены); G2/A/B и девять Rust projections сохраняют прежние условные
границы в исходных ветках. Бюджеты5306/5400(94) и512/1800(1288) не сброшены.
Git merge не доказывает actual helper/merge/Challenge. Подготовленные задания
НЕ разрешают их выполнение в этой CI0-фазе.

# Challenge 8: current checkpoint

Updated 2026-10-07. **IN PROGRESS: [source-linked pointer select completion](SORT4-SELECT-POINTER-PHASE.md).**
Entry `cd44e1bbf115c83c84fd7d4c050b1f74be0e1d09`; new budget
**2398/5400 summed hosted job seconds**, <=1800/job, <=300/proof. No active run.

Accepted: O4 pointer-value model/SAFE constructor, S4b SAFE `as_mut_ptr`, and
S5k typed intrinsic rule at frozen `experimental-source-linked-select-pointer-intrinsics-v2`
/patch `7bb39a84`. S5k/37624082376, source
`128dd5673c7796c5916017ab4afafaeea8d836b8`: all6 positive+10 intended proof negatives
+40 exact admission controls PASS; classifier60 gate+10 wrong-result+28 admission
message mutants PASS; full ctor/asptr/14Rust/C/C++ regressions PASS. S5k was dispatched
before the user's replay-only correction. New semantic extensions now FROZEN;
04d67f4b assume diagnostic patch and unfinished controls are NOT RUN drafts.

Actual intrinsic-on helper source/export/decode/refinement/full31local14BB MIR
certificate PASS; all3 intrinsic calls translated, both ctor/asptr redirects reached.
First proof blocker: `verified/lib.rs(57,9-29): error: No such function:
std::ptr::mut_ptr::<impl *mut T>::drop_in_place`. Whole helper NOT PROVEN; translation
of third intrinsic is not proof execution of its later branch. Drop/forget/assume
remain unaccepted. No ownership/provenance semantic stop has been established.

Independent diagnostics: pointerdrop method fails its stock unwind post; assume-init
S5j invalid ghostclose after Rust tail expression (body NOT entered); corrected
S5k readonly export/decode pass but normal refinement fails `RawPtr: not yet supported`
at bb1 command4, original25/verified33. VF separately rejects local union declaration
`Todo: AdtDef::Union`. These setup/applicability failures do not test read permissions
and do not gate intrinsic acceptance. Refiner and kernel unchanged.

S5r2 replay/37626031885, classifier source
`586c9ae4155a3ad0d3c50ebed2d22d9716a80b4f`, PASS: saved S5j source2454e86,
frozen7bb/v2 only; all3839 manifest entries verified and all6+10+40 reclassified.
Exactly8 reason-only admission corrections; original INCONCLUSIVE classifications
and byte-identical source artifact retained separately. Corrected classifier
60+10+28 plus16 stage/certificate checks and36 replay mutants PASS. No build,
exporter, refiner or proof execution. No evidence transfer across semantic profiles.
[Replay run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37626031885),
[compact replay3.7MiB incloriginal S5j+O4](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37626031885/artifacts/11483952705).

Current checkpoint: requested intrinsic acceptance/replay and actual integration
complete; whole helper remains unproved at drop_in_place57. Further semantic
extension temporarily FROZEN per owner; drafts saved, no new assume/drop rule applied.
Budget **2398/5400** used, **3002 seconds remain in this phase**, no active/queued run.
No automatic continuation of Drop/assume semantic work while this freeze applies.
Runtime/std signatures, kernel and refinement semantics unchanged.

[Latest run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376),
[compact evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376/artifacts/11482879763),
[full evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376/artifacts/11482659442).
Each compact includes O4/37601511894 with byte/hash mapping; original/full O4
preserved. [Design](SORT4-SELECT-POINTER-DESIGN.md),
[results](SORT4-SELECT-POINTER-RESULTS.md). Runtime std/signatures and frozen
kernel/general memory/provenance/aliasing/export/refiner remain unchanged.
RAPx CLOSED / NO-GO; B/C NOT RUN; full sort4 out of scope.

The previous closed phase below is historical, not the current authorization.

Updated 2026-10-07. **CLOSED: [pointer ownership phase](SORT4-POINTER-OWNERSHIP-PHASE.md)**
at the dependent actual callee's storage/borrow boundary.
[Final report](SORT4-POINTER-OWNERSHIP-RESULTS.md).
Entry `e0920ecb07cd05ef08acd6fb5a2fb228af9a1f98`; proof source
`182ddf29dc73961723bf32be6b65643c524ca927`.
[O4/37601511894](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894),
[artifact11473086721](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894/artifacts/11473086721),
profile `experimental-source-linked-maybeuninit-pointer-own-v2`, patch SHA256
`325af428910cff44fb51e8c11ef0e4c9c3ba928c015f1fdf657580745857ca8d`.

**Experimental pointer-value model and SAFE MaybeUninit::new ACCEPTED:**
explicit defined own, checked introduction lemma/body, generated safety prototype,
exact inner/token, no unwind, frame/return/leak; no pointee premises or Copy bound.
Full source/HIR/typed MIR graph certification and all5proof/8source/9MIR controls
PASS. Nonpointer opaque ownership retained;5classifier groups and14 separate
stock/experimental Rust/C/C++ baseline controls PASS. Optional feasibility mode
cannot accept; O4 uses complete acceptance. Runtime std/signatures unchanged.

**Actual select RUN / INCONCLUSIVE:** unchanged N6 source-linked pointer body,
all source/export/decode/refinement gates PASS; SAFE prototype and both constructor
calls at22/23 reached. First remaining blocker:
`No such function: std::mem::MaybeUninit::<T>::as_mut_ptr`, adapter38,20–41.
[Exact reproduction and limitations](SORT4-SELECT-CALLEE.md).
Storage/reference/provenance permissions require a new capability decision;
no alias/borrow/general union/copy/FnMut/Drop/unwind expansion implemented.
Final selected-pointer/frame/no-unwind posts and full sort4 NOT PROVEN.

New budget **518/5400 summed hosted job seconds (8m38s),4 NEW runs**,
<=1800/job,<=300/proof;4882s retired at boundary. Previous budgets not transferred.
No active/queued relevant Actions run; no pending implementation draft.
Final closeout is documentation-only, separately committed/pushed from proof SHA.
Next permitted action: read-only review/documentation. New implementation or
workflow dispatch for as_mut_ptr needs a separately approved named phase.
RAPx remains CLOSED / NO-GO; B/C NOT RUN. No upstream PR/messages/submission.

Earlier accepted components remain separate: stock H_align, index permutation,
rank stability, finite-SWO bridge, scalar ranges ([night report](SORT4-NIGHT-RESULTS.md));
pure SWO composition and exact fieldless layout d4a12525 full matrix
([previous closeout](SORT4-COMPOSITION-CONSTRUCTOR-RESULTS.md)). None supplies
callback/resource/unwind composition or a full Rust sort4 theorem. Their original
source/run/profile identities and failed controls remain in those reports and
EXPERIMENT-LOG. Historical "next" statements do not authorize further work.

Current S5g/37619961051/source53f4d94/ec841d1c: canonical patch audit PASS,
build fails on unannotated decoded guard_type record (`kind` field). No new proof.
S5h adds only D.ty annotation and canonical regeneration; complete matrices
and actual/source-linked read diagnostic remain required. No active run.

S5h/37620410162/source634de56: build fails decoded UInt128 conversion on
cleanup bool switch. S5i uses existing schema-reader conversion, patch7bb39a84.
All numeric APIs reviewed; no new semantic rule. Four independent ghost-only
storage probes added (cast initialized, union initialized, cast none/unknown);
source-linked assume_init export remains separately NOT PROVEN. No active run.

S5i/37621093604/source3d822b0/7bb39a84: build/ctor/asptr regressions PASS.
Pointer-drop body reaches stock unwind post `Cannot prove false` at10.
Assume export requires missing transparent_unions crate feature; admission and
ghost matrix NOT RUN. S5j fixes feature only and collects independent diagnostic
stages without preventing component matrix; any diagnostic setup failure retains
nonzero overall exit. No semantic change; no active run.

Continuation setup checkpoint: run37749632949/c54b9ee3,job113219415885
08:24:37–08:26:47UTC130seconds. Exactusizepatch/stagedspec and consolebuild
PASS; old cache-profile schema rejects newID before matrix. Schema repaired
with requiredusizeinput and samebinarySHA/wholeprofilechecks; no proof claim.
