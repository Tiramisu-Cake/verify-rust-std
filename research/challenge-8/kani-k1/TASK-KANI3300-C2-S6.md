# KANI3300 C2-S6 — оставшиеся контроли, docs, чистка экспорта и freeze

2026-11-15. Worker14, одна стадия. Это верификация корректности, не security-работа.
Подготовлено для выдачи координатором; этим файлом выполнение не начинается. После выдачи — isolated clone
`/root/kani-fix-3300-c2-s6`, ветка `fix/kani-3300-c2-s6`. Existing destination/dirty или wrong base → STOP без reset/stash.
Локальные cargo/rustc/Kani/CBMC/Miri/builds запрещены. Preparation Cloud $0; targeted fork CI и push/dispatch — координатор.
**Gate A на трёх платформах — отдельный шаг ПОСЛЕ S6. Не включать его запуск, полный regression или новый workflow в S6.**
Не менять existing source/PR refs/SEL1 clone и не начинать upstream submission.

## 1. Exact input и принятая S5

- Base **`8d67298c48eb7b2381f806a6353433d1440e3d94`**, tree `5fb7dbaa6f79a75ca552be9d4d5c7b535cf38058`,
  read-only `/root/kani-fix-3300-c2-s5`, fork `fix/kani-3300-c2-s5`.
- Research `4fbb8211aa`: `kani3300/c2-s5/{ORACLE-MAP.md,ORACLE-MAP.json,MODE-COVER-MAP.md,
  MIXED-ISOLATION-DISPOSITION.md,fix-43636027466/RESULT.md,ci-43641978948/CI-RESULT.md}`;
  PLAN-KANI3300-C2.md S6, аудит R4 F9/F10 и ответы1/6/7/9.
- CI43641978948 на8d: fmt/build/clippy PASS; units6/2/9; kani24/0,expected228/0,ui17/0,script2/0,json-handler17/0;
  2 давних fixme ignored (`slices_fixme.rs`, `fixme_unions.rs`). Все4 sensitivity mutations DETECTED с `--force-rerun`.
  Предыдущая попытка43636027466 с2 compile errors/ignored mutation не принятие; её статусы не переписывать.
- S5 переносит21 прежний case/root в22 expected fixtures. Принятое отступление:20 source-single-harness и2 Replace inputs
  с необходимым local `proof_for_contract(passthrough)` companion; `--harness <caller> --exact` выбирает один oracle root.
  Сохранить companion, его domain/contract и позицию flags до `--cbmc-args`; присутствие PFC не означает его execution.
  Не восстанавливать3 JSON suites, не навязывать этим2 файлам прежний lexical one-harness invariant и не ослаблять goldens.

## 2. Границы S6

S6 — tests/docs/export preparation, не новое расширение memory model. Production `kani-compiler`, runtime/library,
driver/shared validator/compiletest, pins U+B1/nightly/CBMC/Kissat и принятые F5/F6/F7 неизменны.
Допустимы недостающие bounded expected controls и их helpers, три документа ниже, точечная чистка нового Part1 test README/comments.
Новый control, выявивший production defect, → STOP с exact repro/ожиданием и предложением отдельного bounded fix,
не переписывать ожидание на произвольный FAIL и не чинить model молча ради freeze.
SEL1/F8 уже имеет отдельные positive replay, но **не входит в C2 scope A**. Не cherry-pick ec85b782a1/другой SEL1 source;
success sort4/swap на нём не переносится на C2. F11 marker invariant остаётся отдельным необязательным пунктом,
не возвращать прежний effect-framework и не делать его зависимостью freeze.

## 3. Оставшаяся контрольная матрица — R4 ответ6

Сначала `CONTROL-MAP`: требуемый путь → existing selector/actual source binding или минимальный новый selector,
ожидаемый native outcome/count/описание/useful witness. Не дублировать уже покрытое и не делать полный T×N×режим matrix.
Новые файлы — смысловые имена в `tests/expected/uninit/`, не research stage IDs. Один selected root на oracle;
documented companion допускается только если действительно требуется проверке stub_verified.

| Обязательство | Минимальная проверка и что не засчитывается |
|---|---|
| Backend-hook intercepted call с shadow argument/return | Legal generated/ordinary call, реально выбранный hook и shadow carrier; отказ pairing/explicit Unsupported, не SUCCESS. Argument/return роли различать; bodyful direct companion должен сохранить supported transfer. Bodyless extern, mock и совпадение имени hook не тот путь. |
| Один Copy-source в двух shadow arguments, с hole | Actual Copy одного place в2 разных argument indices, snapshot source identity сохранён. Достигнутый hole-read каждого индекса/выбираемой ветви и legal initialized companion; не2 разных input objects и не скрытый Move. |
| Fn-trait free function item без/со shadow | Отдельно FnDef через trait shim и принудительно coerced fn-pointer (reuse existing latter). Установить реальный callee kind/layout/protocol; не объявить любой fn-item вызов Unsupported. Shadow-refusal не должен оказаться ранним tuple UnionAsField вместо проверяемого shim/protocol. |
| Padded stride, partial extent через borrowed/raw slice | Valid `&[MaybeUninit<Padded>]` и raw slice/fat-pointer paths; actual stride/field offsets, initialized prefix через границу slot и intended unwritten data byte следующего slot. Legal initialized companion отделяет layout refusal от настоящего hole. |

Backend hook: прочитать `kani3300/c1p/COMPILER-CONTROLS.md#backend-hook-return` как historical specification/UNKNOWN,
не готовый repro. Кандидат — generated PFC/modifies `UntrackedDerefHook`: actual call, selected marker/ABI/body interception,
shadow argument/return и pairing refusal должны быть установлены. Не подменять это source-name match/обычным extern.
Если этот legal path не получен, report NONDISCRIMINATING/UNKNOWN, искать корректную форму; источник новой поддержки не изобретать.

Fn-item: existing fn-trait-pointer cases — настоящие indirect fn-pointer, closure FnOnce — не free FnDef.
Без shadow исход зависит от actual context; задать source-backed oracle и квалифицировать его, не угадывать general SUCCESS/Unsupported.
Для shadow-return можно избегать MU-in-argument-tuple, чтобы не остановиться на существующей aggregate boundary до Call.
Если optimizer превратил требуемый shim в обычный Item, это иной путь и не доказательство shim refusal.

Padded shape: repr(C) tag:u8/value:u32 — проверить actual target layout/stride, не blindly assume8/offset4 на любом target.
Префикс/extent и требуемый bad **data** byte описать явно; padding и payload не смешивать. References только к MU storage,
без invalid initialized &[Padded]/assume_init до intended read. Типичные existing typed-array/byte-slice tests не заменяют оба slice paths.

Повторно использовать S2 coalescing controls/unit9, S3 negatives/reinit и S4 journal/scope unit6/2; не возвращать mixed JSON.
Все новые negative обязаны достигать именно named payload/protocol/boundary failure, без дополнительного frame/layout/validity отказа.
Сохранять portable S5 форму: Checking harness/one selected root, anchored SUMMARY + exact `** N of`, intended Failed Checks,
consecutive useful SUCCESS blocks, verdict. Cover summary не может удовлетворить check count; не pin-ить host/nightly/std locations.
Новый контроль должен различать целевые исходы, а не лишь завершаться каким-то FAILED; non-discriminating setup исправить/явно остановить.

## 4. Docs — действительный scope C2, не SEL1

1. `docs/src/rust-feature-support.md`, Uninitialized memory: описать принятый Scope A из R4 ответа1/PLAN,
   поддержанные top-level slot, `[MU<T>;N]`, `[MU<T>]`, `MU<[T;N]>` для вычислимых masks, raw copies,
   typed moves только data bytes, direct MIR-body argument/return и exact qualified whole immutable masks.
   General limits здесь применимы к uninit-checks вообще, не только к контрактам; дать рабочую ссылку на подробности.
2. `docs/src/reference/experimental/contracts.md`: согласовать с этим scope, сохранить Replace/RecursiveCheck exclusions,
   delayed call cycles и S3 conservative nested aggregate resets/false-positive example. Не заявлять nested transfer support.
   Whole immutable qualification остаётся узкой: unqualified nonzero-subrange/relocation origins могут дать conservative false positive;
   eligible aliases/старые independent static paths могут проходить. Не писать, что все relocation/subrange reads обязательно FAIL.
3. `docs/src/rust-feature-support/intrinsics.md`: заменить stale raw_eq «Cannot detect uninitialized memory» точным
   partial-support описанием для modeled operand byte extents/shadow при `-Z uninit-checks`, включая padding obligation,
   со ссылкой на реальный Uninitialized memory section. Не обещать проверку arbitrary T/layout/origin.

Принятые исключения Scope A не снимать: intrinsics без initialization model (в C2 включая select_unpredictable/hint wrapper),
calls through fn pointers/trait objects, stub_verified/recursion shadow transfer, nested by-value MU/union aggregates и analysis cycles.
Сохранить точную оговорку: `This change does not make core::slice::sort::shared::smallsort verifiable with -Z uninit-checks.`
Fn-item FnDef layout в некоторых shim contexts не описывать как запрет всех function items.
Observed Replace false-positive/boundary fixtures не называть successful mode qualification; Companion PFC не executed от наличия.
Никаких B2/all-T,N/whole-#3300 claims или переноса historical fork results на будущую frozen голову.

## 5. Гигиена export

Проверять только новый Part1 diff от зафиксированной upstream U/B1 и итоговое дерево: не чистить unrelated upstream историю/URLs.
`tests/expected/uninit/part1-edges/README.md` ещё содержит before-CI/MIR-binding инструкции, ссылку на удалённые strong JSON suites
и устаревшее blanket SUCCESS для immutable subrange. Удалить process README либо заменить кратким верным описанием fixtures;
нужную семантику перенести в comments, а внутренние qualification notes — только research.
Убрать из экспортируемой дельты internal run/build IDs, research URLs, coordinator/READY/NOT_RUN инструкции,
handoff/task/status/binding_evidence artifacts и CI-only/sensitivity overlays. Обычная функция `handoff` — не служебный файл.
Не удалять по одному слову/regex: source assertions/descriptions и accepted --harness selectors сохраняются.
Проверить отсутствие dangling imports/links/отсылок к удалённым3 JSON suites; остальные upstream JSON tests/validator сохранены.
Проверить discovery inventory и2 documented Replace exceptions; не потерять required local PFC ради косметики.

## 6. Targeted qualification и freeze

До CI: INPUTS/tree hashes, CONTROL-MAP, source/contract/expected matcher review, `git diff --check`.
Координатор запускает targeted fmt/build/clippy, новые и затронутые expected controls, units6/2/9,
existing Uninit/expected/ui/script и все remaining upstream json-handler, затем тот же bounded Linux Quick.
Использовать actual execution/`--force-rerun` для sensitivity/selector повторов: cached/ignored run не qualification.
S5 четыре sensitivity patches сохранить/revalidate; если S6 меняет их target source/expected, обновить и повторить их через actual compiletest.
Старые два fixme ignored сохранить как pre-existing, новых ignores/skip/check-disable/сужения geometry не добавлять.
Expected228/0 и прочие числа — вход S5, не заранее обещанные новые totals. Новый source/test delta квалифицируется на своём exact SHA.
Stale composition waiver закончился в S5:3 suite удалены по карте, новые expected обязаны проходить; никакого общего FAIL waiver.

После успешного bounded qualification и review зафиксировать **локальный immutable C2 candidate**: exact source SHA/tree,
чистое дерево, test discovery/map, diff от U и от accepted B1, pins/subtree hashes compiler/runtime/tests/docs/deps,
CI receipt identities/coverage, docs/scope и список remaining exclusions. Source/test/docs после этого не менять под тем же freeze.
Подготовить `C2-FREEZE.json`/`EXPORT-MANIFEST` в research, включая base8d, S1–S6 dependencies и targeted run status.
Если выполнение targeted CI ещё не состоялось — `FREEZE_PREPARED / QUALIFICATION_PENDING`, не accepted freeze/ready-to-submit;
координатор принимает immutable голову и создаёт/публикует freeze ref отдельным действием. Gate A3-platform status **NOT_RUN**.
В S6 не создавать gate workflows/dispatch, не выполнять scripts/kani-regression.sh и не запускать SmallSort/SEL1 replay.
После S6 отдельное задание координатора проверит этот же frozen SHA на3 платформах; старые C1b/SEL1 receipts его не заменяют.

## 7. Handoff / STOP

Research `kani3300/c2-s6/`: INPUTS, CONTROL-MAP/MANIFEST, DOCS-SCOPE-MAP, EXPORT-HYGIENE,
DISCOVERY/REPLACE-EXCEPTIONS, REVIEW, CI-REQUEST, C2-FREEZE.json, EXPORT-MANIFEST, RESULT.
Разделить source claims, реальные targeted outcomes и будущий Gate A NOT_RUN. Missing requested control/new defect/необъяснённый
failure → STOP с concrete repro/disposition, не freeze с молчаливо выкинутой строкой. F11 и accepted documented exclusions — не новый STOP.
Source neutral local commit(s), author/committer Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без source push/PR.
Финал после выдачи: `READY <local S6 source sha>`. Не начинать следующий этап/подачу и не менять ветку SEL1.
