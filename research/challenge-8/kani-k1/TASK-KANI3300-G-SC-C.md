# KANI3300 G-SC-C — read-only инвентарь SmallSort, worker 14

**Выдано координатором 2026-11-13; заменяет прежнее задание на controls.** Runtime Codex, одна сессия, **Cloud $0**.
Это верификация корректности, не security-работа.
**Без кода:** никаких guard implementation, новых fixtures/goldens, source branches, workflow/runner changes или запусков.
G-SC worker15 **HELD / NOT ISSUED** до ответа второго аудитора. На сужении scope не настаиваем: инвентарь нужен для выбора.

## Цель и вход

Установить по нашим материалам, какие **SmallSort Select/Merge roots** используют proof_for_contract,
stub_verified, обычные contract Assert/Original и uninit-checks; какие реальные вызовы могут переносить shadow state.
Разделить существующие profile/флаги/результаты и желаемую будущую проверку partially initialized scratch.
Читать AUDIT-BRIEF-KANI3300-PART1-R3.md, аудит PFC-resource @ab75098224 §5 и d1a/ @15276d5723.
Kani semantic reference **4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c**; SmallSort refs фиксировать отдельно.
Не смешивать Kani Part1 с названиями стадий/публикаций SmallSort и не считать разные source trees одним run.

## 1. Инвентарь roots и profiles

Начать с source/docs в g0, /root/verify-rust-std-kani-directbounds и актуальных Select/Merge worktrees;
актуальный repo/ref/task/status установить по их короткому workflow guide, читать большие истории только по нужным разделам.
Найти literal и macro-generated proof_for_contract/stub_verified/ordinary roots, cfg activation и mode-selected callees.
Матрица ROOTS: subsystem/repo/full ref/file:line/root selector, contract target, Check/RecursiveCheck/Replace/Assert/Original,
flags и откуда они взяты (runner/request/fixture), uninit on/off/UNKNOWN, active/experimental/historical, reported evidence.
Положительный grep не доказывает activation; отсутствие flag в одном скрипте не доказывает отсутствие во всех profiles.
Отделить Kani roots от Select/Merge профилей других инструментов: Kani flags к ним неприменимы, не записывать их как uninit-off.

Минимальные известные ориентиры, проверить identities по фактическим файлам:
- RESULT-DIRECT.md: Merge scratch48 PFC, включая merge_scratch48_contract_u8_n9; uninit **off**.
- RESULT-SPECDIAG.md G2: uninit_tail_actual_pfc / uninit_sort4_actual_pfc с uninit **on**, Unsupported до target reads.
- tools/kani_k1.py и scripts/run-kani.sh: штатные флаги и opt-in diagnostic опции; отдельные requests могут их менять.
- verify/{merge,network,helper_contracts*,forwarding_contracts*,insert_tail_contracts*}: реальные annotations и wrappers.
Это начальные ссылки, не исчерпывающий инвентарь и не новая proof credit.

## 2. Source call/effect map для scratch

Для найденных roots проследить выбранный body → constructors/setup → helpers/clauses → call/return boundary.
Использовать тот же критерий shadow-carrying union/MaybeUninit, что инструментер на4f64; source signature-only недостаточно.
Для каждого edge: caller/callee monomorphization и source site, mode, типы аргументов/return, предполагаемый Begin/Store/entry Load/
Store0/normal Load0, что известно из source, что требует actual MIR/GOTO. Не выдавать predicted effect за emitted/исполненный.
Проверить transfer только в requires/ensures/old/helper/generated closure, generic/dynamic/unresolved edges и recursive contexts;
unknown edge отметить UNKNOWN с причиной, не NO_TRANSFER. Полноту обхода/границы inspected graph указать явно.

Отдельно backing geometry: stable flat [MaybeUninit<T>;48], general MaybeUninit<[T;48]>, raw pointer/slice views,
initialized prefix, uninit tail, ownership/lifetime/frame, частичные записи и helper returns. Ничего не переписывать ради модели.
MaybeUninit<[MaybeUninit<T>;N]> и compound/G1 формы — отдельный scope gap, не молчаливое расширение Part1.
Разделить scratch constructor outside Check и operation inside selected Check; whole-harness admission шире path/context guard.
Для каждого root дать влияние **кандидатных** границ: effect-based Check/RecursiveCheck cut, whole-PFC-harness admission,
ordinary-only экспорт; no-transfer доказан source map / возможный transfer / UNKNOWN. Ни одна граница здесь не выбрана.
Replace/stub квалифицировать отдельно; Unsupported PFC не является доказанным контрактом для verified stub.

## 3. Вывод для аудитора

Какие существующие uninit-off результаты сохраняются отдельно от вопроса, какие желаемые PFC+uninit scratch proofs потеряем?
Какие exact roots могут проверить практическую цель ordinary storage, а какие требуют compositional contracts/Replace?
Дать короткие сценарии legal initialized prefix и hole, но **только описания**, не код/fixtures/CI-request на dispatch.
Если exact call graph/флаги/selected mode неизвестны, перечислить минимальные недостающие MIR/GOTO/profile сведения.
Не запускать compilers/verifiers/inventory Builds ради этих пробелов и не выводить полное покрытие из нескольких roots.

## Результат и STOP

В g0 **kani3300/gscc/**: INPUTS.json (repos/refs/read coverage), ROOTS.md или ROOTS.json,
CALL-EFFECT-MAP.md, SCOPE-IMPACT.md, RESULT-KANI3300-G-SC-C.md (≤30 строк).
Только Markdown/JSON evidence inventory; Git/rg и точечная Python-обработка существующих source/research допустимы.
Никаких source/test commits в Kani, code files, local cargo/rustc/Kani/CBMC/Miri/builds/CI/Cloud dispatch,
raw archives/full logs/GCS/credentials, PR/issues или сторонних PR links. Reported/source-derived/UNKNOWN раздельно, proof credit0.
Research [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, stage только gscc/, push g0 без force;
concurrency → handoff без reset/stash/чужих файлов. Никаких будущих implementation задач до решения координатора после аудита.
После инвентаря STOP. Последняя строка: READY <sha research-коммита G-SC-C>.
