# RESULT-KANI3300-P1 — статическая упаковка завершена
Main: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`; upstream local: `c39cc1121cdb287d9d77c38b87cff6c84c2c8046` (один коммит, без push).
v2: `0ab9cc703aed799f6f73d826b60281a4632ab585`; production `81dd85bfce67226e283fdd9a156932e32ece080b`, byte-equal.
Diffstat: production 7 файлов +675/-178; tests/goldens 30 файлов +592; main drift в production-путях отсутствует.
Luna HIGH: блокирующих нарушений shadow/flat-buffer/return0/copy_by_id/frame не выявлено; static only, `REVIEW-INVARIANTS.md`.
15 fixtures ниже; полные build IDs/heads/offsets и исходные observations — `TEST-MANIFEST.json` / `TEST-EVIDENCE.md`.
A=`d5d15c41-1c07-4f9f-a6ff-16c25fae00e1` (U1); B=`45287677-98cb-4dc4-b98d-7ccae4782f5f` (U3 repair1); C=`9f964706-4b89-4340-a1ee-022aa23ecbe9` (U3B).
- `maybe-uninit-wrap-u3-positive/main.rs`: native PASS B,C.
- `maybe-uninit-review-positive/main.rs`: native PASS B,C.
- `maybe-uninit-initialized/main.rs`: native PASS A.
- `maybe-uninit-wrap-u3-padding/main.rs`: native PASS B.
- `maybe-uninit-wrap-u3-source-read/main.rs`: native PASS B.
- `maybe-uninit-buffer-u3-plain-negative/main.rs`: native PASS B,C.
- `maybe-uninit-buffer-u3-clause-pfc-negative/main.rs`: native PASS B.
- `maybe-uninit-buffer-u3-frame-negative/main.rs`: native PASS C.
- `maybe-uninit-partial-copy/main.rs`: native PASS B.
- `maybe-uninit-reset-alias/main.rs`: native PASS B.
- `maybe-uninit-review-argument-return/main.rs`: native PASS B.
- `maybe-uninit-review-overwrite-copy/main.rs`: native PASS B,C.
- `maybe-uninit-review-overlap-copy/main.rs`: native PASS B.
- `maybe-uninit-review-repeat-local/main.rs`: native PASS B.
- `maybe-uninit-review-reset-zst/main.rs`: native PASS B.
Все .rs проверены rustfmt; sources byte-equal v2; 6 goldens переведены на Failed Checks; packaged form NOT_RUN.
Ограничения: nested/arbitrary union, compound storage, typed_swap, select_unpredictable, fn-pointer/no-MIR; PFC OOM.
PFC: clean positive не прошёл по времени; U1 INCONSISTENT/UNVALIDATED; upstream OOM и регрессия не установлены.
Gate PREPARED_NOT_RUN: f046, tree `10c032ab8e3c5a38a3fa639c4b0004d61b7c2ffe`, diffstat2315≤4096, preflight PASS; резерв-кандидат $0.6075, cap$0.80.
Cloud $0, резерв $0; main acceptance и general/independent proof credit отсутствуют; PR draft — `UPSTREAM-PR-DRAFT.md`.
**KANI3300 P1 ЗАВЕРШЁН**
