# Source-only supportability, exact frozen pins

**PROPOSED_NOT_IMPLEMENTED / NOT_RUN.** Full file hashes/commit/ranges are in PROVENANCE.json. Это ограниченный source audit будущего isolation schedule. Why-first trace старого run оставлен W11; harness_runner sorting/старый реальный launch-order trace здесь не исследовались, CI artifacts не скачивались.

| Потребность | Поддержано pinned source | Чего это не подтверждает |
|---|---|---|
| Exact singleton | stock0aac args/mod.rs:254,285: repeated --harness + --exact; call_single_file.rs:126..185 forwards compiler-local selectors, call_cargo.rs:84..122 forwards them to std build; runner d33a runner.py:323 builds stock verify-std selectors/export argv | Порядок multi-selector driver и текущая group policy; A использует один selector за invocation |
| Ordered schedule | runner.py:256 builds groups in execution_groups order; :302 select_groups filters in request order, CLI group list is selection | Порядок rows/export JSON не real launch trace; старый why-first UNKNOWN здесь |
| Continue after failure | runner.py:1197 loops groups | :1203 stores fatal and skips subsequent execution. Local/global separation отсутствует и требует reviewed implementation |
| Per-root scope | execute :563 starts a new process session; :620 samples PG RSS; :463 kills PG; :649 cleanup/reap | RSS6GiB field не фактическое per-root enforcement в grouped call: _run_group :1064 passes group_cap up to12GiB. PG does not cover every setsid orphan |
| Memory ceiling | group_memory_budget :537 computes min(12GiB, available-2GiB) from host/cgroup availability | Hard kernel6GiB limit, simultaneous root metrics и разрешение parallel2 не установлены |
| End-to-end timeout | runner _run_group :1053 applies phase/compile+row group envelope | stock call_cbmc.rs:224 harness timeout surrounds process_cbmc_output, not compilation/instrumentation. A needs root slot deadline beyond inner600s |
| New groups/caps | generic group_rows can represent singleton partition and selected groups | s2_policy.py:30,37,38,60 pins canonical11/one group/600s/7500. check_package.py:81..127 pins workflow. No request-only workaround |
| Shared setup | check_package.py:151 setup/build gate min(900,remaining1800) | Это shared stock tool build, не shared proof codegen между invocation |
| Fresh codegen provenance | _run_group :1045 allocates invocation-specific CARGO_TARGET_DIR; binding_metadata.py:18 retains native bytes and :79 unknown links | Reusing cached metadata would need new binding design; UUID not compiler instance |
| Recompilation cost | stock project.rs:353 recreates dummy crate and calls cargo_build_std; call_cargo.rs:141 constructs target path | Compile-once reuse across harness/stub/PFC/cfg codegen units не обещан. Budget9 root compilations |
| Export completeness | args/mod.rs:906 rejects export-json with only/no-codegen; rich_evidence.py:177 checks complete stock/rich inventory | Compile-only plus detached bare CBMC не supported equivalent pipeline |
| Contract pipeline | call_goto_instrument.rs:25 specializes harness, applies restrictions and contracts | Bare CBMC on an old .out does not retain required transformation/source/origin/decoder bindings |
| Cost ranking | sorting_s2_batch.rs:132 checker negatives concrete, :74 actual swap, :102 witness loops8..16 and32, :29/42 actual merge/assumed sort13 | No measured costs, no causal model-cost inference. Different root shapes can still be expensive |

В PROVENANCE.json line ranges навигационные, не AST/MIR binding proof. Ни источник argv, ни source coordinates не дают independent B1/B2 credit. Все supportability gaps — gates перед будущей реализацией/review, не скрытые утверждения готовности runtime.
