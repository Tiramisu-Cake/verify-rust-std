# KANI3300 C2-S5 — переносимые expected-оракулы вместо трёх JSON suites

2026-11-14. Worker14, одна стадия. Это верификация корректности, не security-работа.
Подготовлено для выдачи координатором; этим файлом работа не начинается. После выдачи — isolated clone
`/root/kani-fix-3300-c2-s5`, ветка `fix/kani-3300-c2-s5`. Existing destination/dirty или wrong base → STOP без reset/stash.
Локальные cargo/rustc/Kani/CBMC/Miri/builds запрещены. Preparation Cloud $0; fork CI, source push/dispatch — координатор.
Не писать в исходные clones/PR ветки/SEL1 worker15. Production compiler/runtime semantics и pins этой стадией не менять.

## 1. Вход и цель

- Exact base **`3b382c812a1b8541946e6dc732cf04497ebcf995`**, tree `716a2446684bb56e0a03b7fbe5df26593648a1c8`,
  read-only `/root/kani-fix-3300-c2-s4`, fork `fix/kani-3300-c2-s4`.
- Research `39f3ec129c`, `kani3300/c2-s4/ci-1/CI-RESULT.md`: baseline43621472749 —6/18 mixed≠isolated,
  additions3/6/9, removed0; candidate43621476331 —18/18 EXACT_MATCH. Unit6/2/9, expected213/0,
  kani24/0,ui17/0,script2/0 и LLBC feature build PASS. Старый bound composition FAIL — не провал нового F7 gate.
- PLAN-KANI3300-C2.md S5, аудит R4 ответ12/F2/F10 и ответ11, actual three suites наbase.

Владелец выбрал expected-файлы. Удалить из export **только** `tests/json-handler/uninit-contract-oracles`,
`uninit-contract-mode-boundaries`, `uninit-part1-composition`, заменив их semantic obligations переносимыми expected tests.
Сначала карта эквивалентности и исходные источники, **потом** удаление; не удалить каталог, а затем выяснять потерянные проверки.
Остальные upstream JSON suites, schema/validator/driver/compiletest matcher неизменны. Не строить четвёртый большой JSON runner.

## 2. ORACLE-MAP — обязательный первый результат

Для каждой прежней case/root и каждой проверяемой особенности указать: old file/JSON pointer/условие,
Rust operation/contract/mode, новый expected selector, exact required failure count/descriptions/useful SUCCESS/cover,
почему операция и достижимость сохранены. Many-to-one reuse допустим только с явным покрытием всех обязательств.
Existing expected siblings часто слишком слабы: одно FAILED/SUCCESSFUL не эквивалентно прежнему JSON oracle.
Переносить/усиливать уже существующие inputs предпочтительнее дублирования; multi-harness inputs split-ить там,
где ими заменяется JSON case. У каждого нового/переработанного oracle-файла ровно один harness.

| Старое обязательство | Что обязательно сохраняется в новой карте |
|---|---|
| Strong p1: closure-zst/scalar-pfc-legal | Legal PFC,0 failures, outer ensures действительно SUCCESS |
| Strong ordinary и pfc: transfer-qualification/legal-pair | Два отдельных harness/files: тело, ensures, returned value и out assertions SUCCESS; PFC legal out-write/frame check |
| Strong lawful-modifies | Legal result29/out29/outside41, ensures и разрешённый out-write без user/private frame failure |
| Strong p2 и postcondition-hole | Два instrumentation failures одного intended read: uninit `*const u8` и `u8`; только конкретный outer ensures может быть дополнительным consequence, не arbitrary FAIL |
| Strong frame | Один intended user outside-assigns failure, следующий разрешённый out write SUCCESS; verifier-private failure не подмена |
| Strong clause | Intended transmute MU<u16>→u16 uninit-read в clause; не ранний protocol/frame/Unsupported |
| Mode replace_ordinary / replace_simple_check | Legal initialized и uninitialized-storage return paths, useful payload assertions и прежние2 source covers |
| Mode recursive_simple_check | Legal bounded/unrolled target, initialized/uninitialized return, base/unrolled-edge reachability; не доказательство рекурсии |
| Mode recursive_ordinary / recursive_check | Единственный explicit interprocedural-cycle Unsupported с читаемым смыслом/provenance; не произвольный FAILED и не legal proof |
| Mode replace_transfer | Ранее observation-only, support unclaimed: отдельно получить/объяснить actual outcome наbase и дать bounded regression oracle; не изобретать mode qualification или желаемый FAIL |
| Composition immutable_legal/hole | Assert(value==17) SUCCESS; hole —2 intended read failures (`*const u8` и `u8`), без extra failures; сохранить различие Some/None |
| Composition ordinary_ensures_legal / pfc_legal / pfc_negative | Relay/return23, legal PFC31, intended PFC payload negative и конкретный ensures consequence, полезные assertions/reachability |
| Composition cycle_root / unrelated_legal_after_cycle | Exact cycle boundary и отдельный legal repeated relay: оба assertions59 и61 SUCCESS; раздельный SUCCESS не доказывает mixed isolation |

Карту строить по source и текущему кандидату, не копировать counts/ID/строки C1b. Например pfc_negative исторически имел3 failures,
а strong p2 допускает2 read failures с конкретным consequence: измерить/обосновать единственное ожидаемое N текущего portable
fixture, не вводить OR «любые2/3» и не скрывать лишний отказ. Не ослаблять исходный contract ради удобного N.
Каждое negative/useful assertion должно иметь target; unresolved строка в этой части → STOP до удаления suite.

## 3. Mixed-root: что сохраняется и что нельзя объявить эквивалентным

Single-harness expected не выражает отношение isolated↔mixed inventories. До удаления отдельной строкой map обосновать:
- F7 production не меняется; structural delayed_scope/journal coverage (существующие6+2 unit tests) остаётся в compiler;
- реальное различающее подтверждение baseline6/18 и candidate18/18 из S4 сохраняется в research со всеми identities;
- per-root semantic obligations переходят в expected, а full-inventory/selector-order/export-schema наблюдения — не proof этого формата.
Допустимо сохранить небольшой portable compiler/unit regression для structural scope/cleanup или минимальный интеграционный
тест штатными средствами, если он не восстанавливает большую обвязку и реально проверяет связь lifecycle с codegen.
Иначе явно обосновать отказ от exported mixed-inventory test: expected не способен его проверить, invariant/units + reviewed
unchanged S4 implementation остаются основанием; residual end-to-end regression coverage уменьшается. Не писать «эквивалентно всё».
Не создавать новую JSON snapshot suite под другим именем, не переносить allowlist T1b и не выдумывать observed AB/BA.
Этот выбор/его пределы включить в REVIEW для приёмки координатором, а не скрыть в списке удалённых файлов.

## 4. Реальная семантика expected matcher и форма goldens

`tools/compiletest/src/runtest.rs`: verify_output/contains_lines ищет **literal substrings**, не regex и не точные строки.
Обычные expected-lines могут совпасть в любом месте; trailing `\` связывает строки в consecutive block.
Matcher сам не запрещает extra output и не считает повторения одинаковой строки: повторить pattern дважды недостаточно.

Для каждого fixture:
1. Проверить `Checking harness <имя>` и single-harness completion. Сохранить нужные experimental flags/режим и per-fixture12 bits;
   без global skip/solver/no-check изменений. `--output-format=regular`, чтобы useful property blocks были доступны.
2. Зафиксировать exact failure count через literal `** N of` в **check summary**, не total property count M.
   Надёжный anchor — consecutive block `SUMMARY:\` затем `** N of`; это не regex. Итоговый verdict обязателен.
3. Каждому intended failure — его `Failed Checks:` description и, где нужно, own target/function/class status-block,
   чтобы чужой user/private frame/Unsupported с тем же N не удовлетворил oracle. Не pin-ить std source location/toolchain path.
4. Useful own body/ensures/harness assertions и нужные разрешённые writes требуют consecutive ID/Status:SUCCESS/Description
   blocks; отдельное слово SUCCESS не доказывает, что нужный check достигнут. Префикс ID/описание должны однозначно
   относиться к роли в карте, без ephemeral closure paths/host/nightly. Если stable block не найден — объяснить другой
   переносимый semantic witness, не выбросить обязательство.
5. В negative-count fixtures не оставлять kani::cover в самом root или copied helpers, чтобы cover summary не давал
   ложного совпадения. Удаление чистого observation hook оформить в карте, сохранив реальный payload/contract путь;
   cover expression с read/side effect нельзя просто стереть — сохранить саму операцию и её oracle.
   Useful cover obligations перенести в positive companion с SATISFIED+Description blocks и anchored check summary,
   либо partition source alternatives в отдельные one-harness files с post-return SUCCESS witnesses.
   Простая замена existential cover на `assert(condition)` для nondet ветки неверна. Generated/original copies:
   требуется реально SATISFIED copy нужного source cover, UNREACHABLE copy её не заменяет.

No blank-only goldens, `.*`/regex надежд, полного stdout snapshot, host triple/nightly/absolute paths/std-line pins,
`--fix-expected` или автоматического blessing. Helper sources не должны случайно обнаруживаться как отдельные тесты
без harness; использовать существующее support/include соглашение compiletest и проверить discovery inventory.
Разделение файлов не меняет initialized/hole setup, out-pointer/frame geometry, actual target/contracts или Move/return семантику.

## 5. Различающий критерий: проверить, что оракулы не тривиальны

Сначала штатные новые expected cases проходят на exact base+S5 test package. Затем отдельные **CI-only/test-only** мутации
с тем же built Kani/compiletest и неизменёнными проверяемыми goldens. Не менять compiler/runtime production для fault injection.
Минимальный finite sensitivity manifest с представительными cases из разных ролей:
- Positive useful assertion удалить из Rust body: verification может остаться SUCCESS, но expected обязан упасть
  из-за пропавшего конкретного SUCCESS-block. Демонстрирует усиление относительно старого verdict-only sibling.
- Negative дополнить независимым reached failure, сохранив исходные failures/FAILED: expected обязан упасть на N,
  а не принять наличие прежних descriptions. Это важнее одного inverted golden.
- Negative исправить (инициализировать hole/убрать outside violation) **или** заменить intended refusal другим failure
  с тем же N: прежний oracle обязан отвергнуть SUCCESS/неверный failure kind/description.
- В отдельной временной копии golden инвертировать N/verdict или required SUCCESS→UNREACHABLE: actual matcher обязан reject.
  Последняя проверка — sanity, не единственное подтверждение нетривиальности.

Для каждой мутации записать selector, exact patch/hash, predicted и observed native verdict/failure N, expected mismatch reason
и exit actual compiletest. Intentional mutant-selector FAIL — успешное испытание oracle, не штатный test PASS.
Build/setup/timeout/compile error/другой ранний Unsupported не считается detection мутации; variant переделать.
Не ограничиваться самодельным Python matcher: использовать actual compiletest в CI. Переиспользовать сборку, не делать
полный Kani rebuild/full gate на каждый mutation. Все overlays/мутации/инвертированные goldens остаются вне export.

## 6. Удаление и приёмка

После завершённой ORACLE-MAP и review переносов удалить только3 названных suites/их Python/JSON fixtures.
Сохранить нужные Rust helpers в new expected layout и research evidence; не снести общие scripts/validate_json_export.py,
актуальные upstream JSON suites (#5154), S4 units и независимые existing expected controls. Не оставлять dangling imports/docs.
Не дублировать без нужды прежние expected selectors; inventory before/after объясняет каждый удалённый/новый selector.
До CI — source/contract/flag/map review, literal matcher audit, `git diff --check`; local compiler/verifier не запускать.

CI-request координатору: fmt/build/clippy, new/reworked expected + sensitivity manifest, existing Uninit/expected/ui/script,
S2 immutable/S3 reset/S4 cache units и остальные upstream json-handler suites. Затем existing Linux Quick.
Known bound composition FAIL больше не переносится как waiver: suite удалён после map; замены обязаны пройти.
Unexpected negative/UNREACHABLE useful check/ошибка discovery/потеря unmapped obligation → STOP.
Общий3-platform full Gate A остаётся после S6/freeze; не заявлять переносимость уже исполненной на3 hosts по одной Linux проверке.

Research `kani3300/c2-s5/`: INPUTS, ORACLE-MAP, MODE/COVER-MAP, MIXED-ISOLATION-DISPOSITION,
DISCOVERY/DELETION-MAP, SENSITIVITY-MANIFEST/RESULTS, REVIEW, CI-REQUEST, RESULT с NOT_RUN/UNKNOWN где нужно.
Source neutral local commit(s), Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без push/публикаций.
Финал после выдачи: `READY <local S5 source sha>`. Не начинать S6 и не переносить SEL1 в C2.
