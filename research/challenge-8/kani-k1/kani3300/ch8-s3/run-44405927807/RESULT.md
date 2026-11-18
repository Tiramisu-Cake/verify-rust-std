# Run 44405927807 — exact BEFORE comparison

**READY:** frozen `fc29b93b1e333b73e55e2872701c80d9927f3b02` rejects two **path strings**, while all three recorded binary SHA-256 values match across controller E0/pre/post and worker BEFORE/AFTER. Authentic local rejection reproduced; exact local/upload-only collector results agree. See [BEFORE-DIFF.md](BEFORE-DIFF.md) and machine-readable comparison.

`kani_driver.path` and `kani_compiler.path`: controller `tool/target/kani/bin/…`; worker `/home/runner/work/kani/kani/tool/target/kani/bin/…`. Physical same-file identity remains UNKNOWN because realpath/readlink/stat data were not recorded. No byte drift, rebuild, installation or symlink cause is established.

Native job **completed/failure**; campaign **STOPPED**, completed prefix **0**. First campaign row remains **INTERRUPTED/UNKNOWN**, eight selected rows **NOT_RUN**, eight deferred obligations **NOT_SELECTED**. The compact native export nevertheless records first-root **FAILURE at S2_NEG_CHECKER_ORDER**, exit1 and verification0.045636733s; this supersedes the coordinator's provisional “no native verdict” observation. It does not admit the unsealed row. Eight UNREACHABLE checks remain visible; reject-ALL-U stays enabled.

254 bounded integrity/identity/reader checks passed. Qualification0, obligations closed0, independent B1/B2 credit NONE. No patch applied. Root reviews this committed intake, then original13 repair/regression, same14 delta, newGO.

Budget remains coordinator-reference **31/31 + 11/17 = 42/48**, case-specific charge0 under ledger `01f36372c07082a1cd592f29fe5702606926112b`. No blanket refund rule or accounting recalculation. Only this owned intake directory changed; no source/control/tests, compiler/CI/push/ledger/subagents/model/settings actions. High/Fast OFF preserved.
