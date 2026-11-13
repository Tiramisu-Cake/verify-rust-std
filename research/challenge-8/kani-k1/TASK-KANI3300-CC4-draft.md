# KANI3300 CC4 — cycle attribution and two expectation corrections (DRAFT / NOT ISSUED)

2026-11-13. Это верификация корректности, не security-работа. Одна bounded preparation/diagnostic stage после отдельной выдачи.
Сейчас **не выдан**: никаких source changes/веток, CI/сборок или source push по этому документу.
После выдачи local cargo/rustc/Kani/CBMC/Miri/builds запрещены; Cloud $0; review/push/CI/caps — координатор.
Не читать произвольные raw logs/архивы; использовать curated findings и точечные данные, явно переданные координатором.

## 1. Exact base и предел стадии

Source CC3 `76a706f8f8c5b0471bd5c8e6b48cdaf45bab9b66`, tree `6730468d0cb9cf24752ad67ef6ebaab35be8e627`.
Reference `/root/kani-fix-3300-cc3` read-only; после выдачи isolated clone/branch `fix/kani-3300-cc4` от этой головы.
Dirty/wrong base → STOP без reset/stash. Research g0, вход `5d41873ec499cd460f4c70ce080a5b4528e8a8b8`.
Прочитать `PLANNER-CC4-REVIEW.md`, cc1/cc2/cc3 handoffs, mode-findings и actual mode-boundary sources на CC3.

Цель: исправить2 неправильно предсказанных expected outcomes и установить точную природу reported cycles,
особенно у **source-nonrecursive** SimpleCheck companion. Не реализовывать fallback/SCC/новую shadow policy.
CC1 no-partial-graph guarantee, CC2 scalar/ref slots, CC3 upvar masks, A3/M1/S3/private frame и8 сильных оракулов сохраняются.

## 2. Применить готовую точечную правку expectations

Artifact `kani3300/s3-compat/cc4/expectations.patch` рассчитан на exact CC3; до apply проверить diff/check/hash.
Только:
- `tests/expected/uninit/closure-zst/capture-reference-legal.expected`;
- `tests/expected/uninit/closure-zst/capture-union-reference.expected`.
Rust inputs/остальные goldens неизменны. Для каждого: Checking harness, точный Failed Checks reason,
VERIFICATION FAILED и summary0 successful/1failed/1total. Не менять на общий FAILED или произвольный Unsupported.

CI43453928092, локальный лог координатора cc3-r1.log дал exact reasons, уже записанные в patch:
UnsafeCell<MaybeUninit<u8>> contains union as a field; dereference on union field.
Первый не достигает полезного closure body, второй останавливается на union-field access. Такие cases — boundary regression,
не capture/PFC proof credit. В CI отдельно подтвердить failure class/источник/полное множество из1 failure и отсутствие лишних.
Существующие .expected — output matching; приёмку не ограничивать тем, что substring совпал.

## 3. Cycle provenance и изоляция

`recursive_simple_check` проверяет bounded_transfer; его body не рекурсивен. Не записывать заранее expected Unsupported
по имени root/file. Сначала для recursive_check, recursive_ordinary и recursive_simple_check получить:
exact entry Instance → actual selected body → caller callsite → callee Instance → repeated active key.
Путь нужен для каждого root отдельно, с обозначением обрезанных частей. Текст Debug Instance, обрезанный192 chars,
или один `overridden=true` не достаточны для классификации registration cycle.

Добавить минимальные bounded диагностические метаданные к имеющемуся CC1 пути: exact monomorphized identity,
typed provenance **Source / RegistrationOverride / DiscardedClosureOverride**, selected-body identity и caller location.
Семантику анализа не менять. Не строить новый trace/export framework и не расширять публичный JSON schema.
Если имеющегося complete path достаточно, новые code changes не нужны; если не хватает — передать конкретный запрос
координатору, не скачивать весь artifact/log. Existing typed source/selected MIR windows достаточны, если замыкают цикл.

Контроли для будущего CI-request:
1. Original3 roots в recursive.rs, singleton/--exact, с сохранёнными исходниками и отдельными полными inventories.
2. Extract **bounded_transfer + только его helpers/contracts** в standalone fixture без recursive sibling;
   оставить bool/MU predicate/captures/body без semantic changes. Это обязательный legal SimpleCheck positive,
   не новый arbitrary Unsupported golden. Compare original-vs-isolated selected-body/cycle path.
3. Actual recursive_transfer с его helpers/contracts в standalone ordinary fixture; classify genuine body/registration cycle.
4. Original/mixed root orders, singletons, completed DAG/repeated-callee controls — fresh active contexts и exact root association.
   Общий overrides map не считать автоматически corruption, но проверить mode/body selection per unit.
5. Ordinary/Assert и SimpleCheck для nonrecursive replace fixtures, P1 и8 сильных oracle cases — прежние PASS/no-extra-failures gates.

Если bounded isolated root проходит, а исходный нет — искать unit/mode/body-selection разницу, не менять scope по имени.
Если isolated тоже даёт цикл — предъявить actual generated/helper edge; source-nonrecursive не означает автоматически acyclic MIR.
Ошибочный source/mode body можно предложить заменить mode-selected **pre-UB** representation отдельным reviewed fix,
но не брать instrumented runtime bodies рекурсивно и не подменять generated call исходным panic.
При необходимости новой snapshot/pass архитектуры — STOP с минимальным diff/design proposal, не расширять CC4 молча.

## 4. Scope wording — только по установленному факту

Draft doc replacement вместо “Ordinary calls ... are not affected”:
“With -Z uninit-checks, a harness is rejected as unsupported if delayed initialization analysis encounters an
interprocedural call cycle. This can affect ordinary proof harnesses and proof_for_contract checks; a runtime recursion
bound does not bound this analysis.”
Сохранить отдельную границу Replace/shadow-transfer. Не заявлять Unsupported любого recursive attribute при отсутствии
реального analysis cycle и не переводить scalar/ref обычные closures обратно в неподдержанные.
Текст descriptive; широкая новая граница обычных контрактов требует решения владельца и representative verify-std inventory.
У required nonrecursive SimpleCheck unexplained Unsupported по-прежнему BLOCKED; документация не закрывает этот gate.

Не retry-ить root с source panic-body register. Даже при fresh graph/body map это может потерять seeded aliases/checks/setters.
Для разрешённого fallback нужны самостоятельное доказательство conservative summary и matched negative controls;
«как upstream», регистрационный marker или устранение crash этим доказательством не являются.
При настоящем необходимом цикле дальнейший выбор — sound summary/SCC либо явно согласованный scope, не silent cutoff.

## 5. Optional upstream flat-recursion probe

По source exact upstream `bf9c58e662fd65c64381ef2ac97a6397ffc0693a` имеет тот же негардированный recursive run;
фактический upstream crash пока NOT_RUN. Не использовать experimental HEAD24 commits aboveU как baseline.
При отдельном GO можно предложить один tiny raw-pointer/u8 recursive helper без contracts/MU/union и paired current root:
valid initialized caller, finite runtime depth, inline-never, preserved static self-call и reached delayed-UB seed.
Если seed/edge удалён оптимизацией или раньше другой Unsupported, case NONDISCRIMINATING. Только named stack-overflow
с точным binary/source связывает execution claim; current должен давать explicit cycle Unsupported без compiler crash.
Новый upstream build/дополнительный solver/run не обязателен для CC4 и не включён в прежние разрешения автоматически.

## 6. Handoff/STOP

Research `kani3300/s3-compat/cc4/`: INPUTS, CYCLE-MAP, CONTROL-MAP, EXPECTATION-BOUNDARIES,
CI-REQUEST, REVIEW, RESULT≤35строк; исходный expectations.patch сохранить как отдельный artifact.
Документировать optional/unexecuted cases и какой cycle реально найден; historical cc3-r1 outcomes не переписывать.
CI-request использует normal checks/solver/slicing/object-bits12, existing bounded capture и predeclared roots/caps;
coordinator запускает targeted stages, затем общий Quick/strong JSON gates на reviewed composition. Здесь CI не запускать.
Source package — отдельный reviewed commit(s) от exact CC3, author/committer Tiramisu-Cake <igkharin@gmail.com> через -c,
без push/CI overlays; research [skip ci], stage только CC4 results/docs, без push/следующей выдачи.
SimpleCheck cycle без attribution, потерянные checks, лишний FAIL или сбой source selection → STOP/BLOCKED,
не изобретать golden для общего успеха. Сейчас **DRAFT / NOT ISSUED**.
