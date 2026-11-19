# Fresh W11 #4591 review — sealed handoff

**REQUEST_CHANGES.** Root must verify this exact committed packet before assigning W15. The review requests seven meaningful harnesses across six test artifacts, with an exact named disposition for all 38 current harnesses and all three expected fixtures. It does not authorize source implementation, CI or publication.

- Task g0: `58a74e7436c8214652708bda480f1f9eccd4ad5c`.
- Reviewed base: `969f4648980a8e66cd0ca32fd3e714a55ac32cef`.
- Published source: `031fc085cd4373b5fc93a55128d5a69fdbd88df1`.
- Tree: `2ff34bc99ec3fe63579202c196f0ca288e318919`.
- Sole parent: `6fca00af805b5c62b58e3e3f29eef183d6939907`.
- Clean same-tree local read source: `f82934ca97caaa1270d5279054aa950173868be5`.
- Source full-index diff SHA256: `b0799ef2f4b96ef2e3adc84db4a61a2e4f1301c5aba30d2c60ea690fcf80056f`.

REPORT.md records compiler assessment, five actionable review findings, open overlap/alias limitations and native evidence boundaries. COVERAGE-EDITS.md is the concrete W15 recipe: share the ordinary requires/ensures/both, recursive/generic/transitive controls; retain provider PFC, verified-provider and single-call caller-PFC controls; reduce the semantic negative to one caller harness with reachable provider pre/post failures; preserve the issue4591 caller-overflow repro verbatim; delete the overlap diagnostic pair; retain one honest no-assert harness and remove its three orthogonal controls. The three compiler paths remain byte-exact frozen; no exception is proposed. No historical packet or source file was edited.

PROPOSED-PR.md contains exactly two English substance paragraphs, Resolves #4591, the exact license and AI disclosure, and one new full-standard-CI placeholder. It stays inside this review; the owner external draft was read and hash-verified, never written. The placeholder remains pending actual authorized CI. The current native aggregate remains Kani FAILURE, Format/Deny SUCCESS; named harness/property results remain UNKNOWN. Cleanup native execution is NOT_RUN. Perf infrastructure attribution remains coordinator-reported, independent cause UNKNOWN; no performance speedup or complete-green claim.

INPUTS.json seals task/snapshot provenance and the original pinned contract. STATIC-CHECKS.json records all eleven changed-file identities, all 38 declarations, protected-tree/dependency/owner-text matches, whitespace and bounded arithmetic checks. These are source/static checks, not native proof. The review was performed directly with settings unchanged; no subagents, compiler/native tools, CI, push, publication, raw logs, archives, GCS, ledgers/accounting or S4P2 work occurred.

MANIFEST.json contains SHA256 and byte length for every other file in this directory and excludes itself. The containing local g0 commit seals that manifest. Its full 40-character SHA is reported in the delivery message, rather than embedding a circular self-pin here. Verify committed blobs against the manifest, then bind W15's future candidate to parent031 and this review. W15's package requires independent review before a separate root/coordinator GO. No new candidate or future CI head has been created by W11.
