# S1-07: что сохранить для офлайн-приёмки w11

Вход S1-06: run `43889560779`, std `5be85699b8826e3286c0bf89efb9affefac0acb5`,
tool `0aac16ef62da9e9d5645782d458593e5d78143ba`, executed control
`a14a513eb7a77297a0cc10ff6eefa7577c2c383c`, request SHA256
`0ff35bdc40434ac6b22b4f4b5919923ab09d849c08c9930f291c014f8b96fe7b`.
Ниже перечислены недостающие связи/измерения; предлагаемые имена новых полей
обозначены кодом. Наличие metadata само по себе не закрывает proof obligations.

1. **After fingerprints: 10 групп / 26 строк.** Отсутствует
   `tool_fingerprints_after.binaries.{kani_driver,kani_compiler,cbmc}.{path,sha256}`
   и `required_hashes_present=true` для `activation-override-u34`,
   `light-controls-u34`, `freeze_copy_u8-n01-u34`, `freeze_copy_u8-n23-u34`,
   `freeze_default_noncopy-n01-u34`, `freeze_default_noncopy-n23-u34`,
   `stable_freeze_u8-n01-u34`, `stable_freeze_u8-n23-u34`,
   `unstable_freeze_u8-n01-u34`, `unstable_freeze_u8-n23-u34`.
   Нужны before/after **одного нового invocation** для fixed required set;
   текущий hash, source_after и другой run after не заменяют измерение.
   Делать after в защищённом finalization после остановки child, до rich validation,
   включая error/timeout/partial export. Сохранять исходные
   `execution.original_exit_code`, signal/timeout, original exception отдельно от
   `snapshot_errors`, список required/missing binaries, фазу и завершение snapshot.
   Null/wrong type/missing/drift остаются UNKNOWN. Source/variant cleanup сохранять.

2. **Resolved PFC target → wrapper: 22 строки.** Source attribute и export target
   связаны; непустой `contracted_function_name` — по pinned producer символ
   **modifies-wrapper**, а не самостоятельное подтверждение impl. Нужен
   `compilation_id` и для каждого `(group_id,row_id,crate,harness)`:

   - `harness_instance` (DefPathHash либо равнозначный стабильный ключ,
     crate disambiguator, substituted types);
   - `resolved_target` (canonical fully qualified path, trait, Self, F и прочие
     substitutions, selected specialization impl identity, target FnDef/instance);
   - `contract_resolution` с ребрами target → check/checked_with →
     modifies_wrapper → emitted `contracted_function_name`, с instance identities
     и исходными attributes/spans;
   - effective requires/ensures/modifies clauses, их definition/expansion spans,
     wrapper/target call edges и связи с exact property IDs (включая post/frame).
   Существующие candidate sites и точные gaps по каждой строке:
   [ACCEPT.json](ACCEPT.json), `pfc_analysis.bindings`.
   Не определять выбранный impl по terminal name, номеру closure или ordinal.

3. **Placeholder assertions → исходные сообщения: 111 связей / 21 root.** Для каждой неоднозначной
   записи `semantic_binding_gaps` типа `success_property_binding` сохранить
   `assertion_origin`: exact property ID/class/status/description, owning
   harness/function instance, expanded assertion expression, definition span,
   callsite span, macro expansion chain/instance и substituted arguments.
   У `smoke!`, `smoke_exact_n!`, `positive!` несколько assertions схлопываются в
   один callsite с одним placeholder-текстом. Нужна связь с конкретным assert,
   а не глобальная уникальность literal и не последовательность ID.
   Три сообщения generic helper `inactive<T,F>` уже связаны с полными наборами
   exact SUCCESS IDs его трёх экземпляров; сохранять эту связь с вызовами и в
   новом run. Сохранить original placeholder;
   отдельное смысловое имя не должно подменять description.

4. **UNREACHABLE: источник и применимость.** Все 413 checks + 2 covers перечислены
   по `(group,row,harness,property_id)` в `unreachable_analysis.records`.
   226 checks объяснены exact source/domain правилами; два negative covers
   разрешены отдельно. Осталось 187 UNKNOWN checks: 133 dependency-site
   applicability и 54 post-predicate origin/binding. Для них сохранить `property_origin`:
   originating function/MIR instance и block/statement, source expansion span,
   contract clause/wrapper instance либо обычный caller, call edges до target,
   path/branch predicates с привязкой к N/type/trait и assumptions данного root.
   Это должно различать bounds/overflow check внутри `active_post`, actual
   relation assertion и обязательный участок. Для `active_post` особенно важно
   различить вызов из target ensures, независимого caller/canary и model control.
   Для macro-generated bounds checks нужны definition span и выбранная ветка
   expansion; source line/callsite сами по себе этого не устанавливают.
   Точные unresolved sites (пути относительно `library/core/src/`):
   `fmt/mod.rs:820` (28), `num/uint_macros.rs:3222` (25), `:3224` (25),
   `:3916` (12), `ptr/const_ptr.rs:1479` (25), `ub_checks.rs:148` (18);
   в `slice/sort/shared/smallsort/verify/sorting_model.rs` — `:97` (12),
   `:100` (5), `:106` (5), `:111` (10), `:112` (10), `:113` (5), `:118` (7).
   Exact IDs, monomorphizations и row/group для каждого случая находятся в receipt.
   Если после binding выясняется mandatory post/frame/relation либо обязательный
   участок со статусом UNREACHABLE, это blocker, а не исключение по helper-name.

5. **Covers, negatives, companions и N0..3.** Сохранять полный exact stock/rich
   inventory и существующие predeclared required messages/IDs/oracles/companions;
   для covers — expanded predicate, выбранный macro arm, assumptions и позиции
   actual call/return/post/frame. Два return covers после предобъявленного
   activation failure допустимы только с exact sole-failure oracle и успешным
   same-run production companion; positive vacuity credit они не дают.
   Сохранить все четыре N-member каждой из четырёх replacement unions в одном
   совместимом новом run. SAT/счётчик не доказывает полноту domain.

6. **Связность metadata и ошибки collector.** Для новых связей нужны общий
   compilation/export identity и SHA256 входных source/tool/config/variant,
   relation к group invocation и exact selector/crate. Сохранять argv и effective
   cfg/checks/unwind, original exits/exceptions, полные rich records и manifest
   digest/bytes, даже при отказе rich validation. Нельзя склеивать одинаковый
   selector между production и mutant группами: ключ включает group и row.

**Location exception не требует отдельного proof.** В S1-06 она применена только
к 18 exact tuples / двум ID из [LOCATION-POLICY.json](LOCATION-POLICY.json).
В S1-07 decoder/collector должны сохранять оригинальные null file/line и
`lib.rs:0:0` display, ID/class/description/SUCCESS и согласованно применять только
разрешённое location-only правило. Иные missing sites fail-closed. Checks не
удалять, historical receipts не менять. Отсутствие старых after не исправляется
задним числом. Этот список не разрешает dispatch и не обещает acceptance S1-07.
