# Combined scope and integration question

Destination: [verify-rust-std #56](https://github.com/model-checking/verify-rust-std/issues/56). Owner-only draft; post once here, not also in #752.

---

Following the [answer on primitive types and default ordering](https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2611410906) and the [challenge requirements](https://github.com/model-checking/verify-rust-std/blob/25b2b24c82a960734a2bab082784747b9b785177/doc/src/challenges/0008-smallsort.md), we read item 2 as checking actual trait-method contracts for sortedness and multiset preservation over every valid caller length: fallback up to 16, general/network up to 32, using primitive values with their usual ordering. Our proposed coverage strategy uses symbolic lengths and accounts for all six implementation bodies, including specialization and forwarding routes. Those are our coverage choices, not a claim that a particular harness count was prescribed. Please correct this interpretation if needed.

Could you clarify the remaining scope and integration points together?

1. Does item 1 additionally require insertion-helper safety for valid lengths and offsets beyond all SmallSort caller thresholds?
2. Would checked primitive instances plus `Cell<u8>` and a non-Copy wrapper as route representatives, with six-body accounting, meet the intended type coverage? Which additional instances would be required?
3. Which total time, worst-shard time, peak RSS and concurrency budget should we target? May selected harnesses run in a separate `-Z uninit-checks` safety step? Item 2's proposed sorting work has uninit/value checks OFF; that proposed safety step is separate, and any later `-Z valid-value-checks` step would need its own qualification.
4. Upstream `main` currently pins Kani `c5e65fdfc3e15ec32293f2a4c07509aebec033c9` ([configuration at the checked revision](https://github.com/model-checking/verify-rust-std/blob/6079edcda31accaf396b883f3f38e2581d0710d7/tool_config/kani-version.toml)). Could it be bumped to **clean upstream Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`**, which contains the [#4908](https://github.com/model-checking/kani/issues/4908) and [#5116](https://github.com/model-checking/kani/issues/5116) fixes, independently of the pending [initialization series](https://github.com/model-checking/kani/issues/3300)? The current [#752](https://github.com/model-checking/verify-rust-std/pull/752) head `872d5a43380752786415bc00d2a12ce0e930cb37` still uses nightly-2026-10-22 and predates merged [#745](https://github.com/model-checking/verify-rust-std/pull/745), which updates to nightly-2026-10-23. A pin-only change there fails to build with `0aac`; merging upstream `main` is required first. What adoption route should we follow? This requests adoption; neither the bump nor a separate safety step is reported as adopted.

*Disclosure: this message was prepared with the help of AI assistants.*
