# KANI3300 U3 — независимое статическое ревью delta

Reviewer: GPT-6 Luna HIGH, отдельный контекст, без вложенной делегации.
Candidate `8bfb7c7c908fe58668214089a0fc7d1b5ccfe378`, baseline U1 `546bcf30379b9b2894f94b1305d5277cc5b4574c`.
Patch SHA-256 `22b82d251006b83384cce1da644ca8842cd0fdb4ee98ed4c701d8817c5372a08`; pin `f046b70644e113be0df9c22c2e6ea44a65a57566`.
Ревью 2 production-файлов v2 − U1, новых fixtures/goldens и нужных исходных dependencies.
Вердикт reviewer: конкретных production findings не выявлено; это статическое ревью, не proof/native credit.

- Exact matcher требует T / длину N и одинаковый размер. Единый SetStorage использует data-mask T; padding false.
- Обычный super_rvalue сохраняет проверки typed source; delayed-UB instrumentation не заменяется новым assumption.
- Составные storage-формы с union остаются Unsupported; select_unpredictable не менялся.
- Buffer — поле существующего marked MEM_INIT_STATE. Existing contract.rs добавляет этот ghost-объект в assigns;
  пользовательские modifies targets/проверки не меняются. Изменений общего DFCC/contracts нет.
- Store сохраняет object ID/offset до завершения source lifetime. Return transfer не читает мёртвый указатель;
  copy_by_id/bless_by_id сохраняют алгоритм nondeterministic byte witness.
- Matching Load проверяет layout_size, переносит и очищает buffer; mismatch оставляет его следующему индексу.
  No-MIR guard отказывает до создания StoreArgument; Forget сохраняет явную прежнюю no-effect модель.
- 14 U1T-файлов проверены против `647109cf6342474d899aa463315a37dac14fd831`: неизменны.
- Fixtures содержат padding/source-read, nested/two-argument/return0/stale, clause/plain/PFC и frame controls.

Ограничения: Rust/Kani/CBMC не запускались. Native NOT_RUN; clause/PFC positives и конкретная следующая
диагностика полного IntoIter не подтверждены. После native PASS — отдельное независимое review координатора
по TASK; этот readiness review его не объявляет выполненным.
