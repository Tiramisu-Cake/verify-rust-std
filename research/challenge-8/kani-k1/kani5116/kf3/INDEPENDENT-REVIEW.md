# KF3 independent review

- **Verdict:** No static findings in the reviewed candidate; all scoped invariants and controls checked are satisfied.
- **Baseline:** `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`
- **Candidate:** `a139af7ac47b794eaf7b8bdcae52a7ba0a866fea` (tree `661997d105b3c6aa565d4e26915c6fa852e97e3a`), one commit over baseline.
- **Packet identity:** handoff SHA-256 `8b631732432baa466bb8760c616f5189a659b764d2b45ad10c5a4f91a335a3ec`; diff SHA-256 `11c981216337d5c4b786bfc9a70ff96439ec9b40a2de560fcfb7febb145fced4`; packet `spec.json` SHA-256 `c57cc5bd026506e7486995374847136de7bdc131b12859efc5a44f2cfc1bd114`. All files listed in packet inventory independently match their declared SHA-256.
- **Production:** candidate production delta from `2a3e2ae19cd1dc4a50f53b1283e7bcf215cb81d9` is exactly the supplied `ImplItemFn` patch (SHA-256 `0921813bdd50693e378b71c8ea85a109ab2bcbbec2f1234d97cfbdff1e4ee443`); reverse `git apply --check` succeeds. No other production paths changed.
- **Static checks:** no-body trait guard remains; unrelated `ItemFn` parsers remain; `handle_untouched` keeps inner attributes in the same emission position. All `annotated_fn` consumers use compatible `ImplItemFn` fields (`attrs`, `vis`, `defaultness`, `sig`, `block: Block`); `Cargo.lock` pins syn 2.0.119. Syn's parser and `ToTokens` retain inner attrs within the block and print `defaultness`.
- **Tests 1–4 / controls:** negative requires fixture retains PFC, `stub_verified`, `check_invalid_caller`, `value != 0` expected failure, and adds `--no-assert-contracts`; clauses fixture consistently uses `requires_first`/`modifies_first`, with PFC and verified-stub harnesses for both orders. Existing regressions are retained; duplicate-name comments are absent and generic #4908/#5135 comment remains.
- **Commit metadata:** author/committer `Tiramisu-Cake <igkharin@gmail.com>`; original title retained; no Co-Authored-By, internal-stage, or skip-ci marker.
- **Limitations:** static review only. Builds, compile checks, formatting checks, Kani/CBMC execution, and behavioral tests are **NOT_RUN**.
