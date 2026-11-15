# Profiles OFF on P′ — coordinator handoff

One fixed62-row OFF qualification request; exact pins/hashes/caps in CI-REQUEST.json.
Source9fa2f7f97760584f38738909625c064006d8a936 is a single cherry-pick of b5cf722e20 on P′c5ff36ff433692140605891f646043f991db05de. Migration patch and its five review dependency blobs are unchanged. Source tool_config keeps upstream pin; OFF runner uses its separate exact stock0aac tool with external config, as before.

Control6269319aecfb3328a2cffe8e2779432dbc346322 has a single stock0aac parent. Manifest,62 rows, ordering, checks, negative oracles, runner caps and ON deferral are unchanged. Changed pins bind the new source/tree. Fallback now removes list/target in addition to row targets; upload excludes **/target/**. Original receipts/exits and list diagnostics survive.

This package grants no dispatch, push or ledger authority. All new CI and proof results are NOT_RUN; credit NONE. See HANDOFF.md before any separately authorized coordinator action.
