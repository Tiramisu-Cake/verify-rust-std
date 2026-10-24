# Select R24 tool overlays

Base: upstream VeriFast `f76012fb518703b1d98e243ac4f487f16877cfcb`. Apply the rows below in order. Rows 1–27 are the const callee chain from reviewed candidate `a4737f9febf20ec5373eafa641268c26c6e674c7`. Row 28 is an R24-only AST diagnostic utility overlay, submitted in Build `0d214997-138c-41ea-abcf-b337cffb8c72` with result pending; the normal verifier/translator semantics are unchanged.

Base translator SHA-256: `c1eb897673f88b0b8dc50798deca603bdad2c60818b6d5380ccf1dda055fe445`. Final translator SHA-256: `103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44`. Final parser SHA-256: `6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246`.

Static patch application against committed base files reproduced these hashes. No local compiler, exporter, MIR decoder, source preparation or verifier was run. R24 Builds af904556 and 234e58e3 did not accept the callee; row 28 is now submitted, with its hosted result pending. This document grants no proof credit or profile acceptance.

## Gating and scope

The callee runner accepts the existing R20/R21 route literals; R24 uses the R21 route marker plus its separate session phase and fresh ledger. Exact per-call opt-ins remain closed: `SORT4_R20_FINAL_SELECT_REPAIR=1` and fractional admission are set only by the existing proof entry, after source/unit/body and snapshot checks. The default route remains unchanged.

The frozen O26 manifest supplies rows 1–20; the O26 refresh profile supplies rows 21–22. Row 23 selects refreshed branch certificates under the existing final-select repair gate. Row 24 is the cumulative R23 fractional-forget patch (the R21/R22 fractional patch files in recipe closure are dependencies, not additional apply steps). Row 25 refreshes admitted fractional MIR coordinates. Row 26 updates erased synthetic ghost-command successor accounting only for admitted fractional `select_unpredictable`; it does not change the dead-code checker or real-call unwind edges. Row 27 repairs coefficient/type-predicate parsing and leaves the translator hash unchanged.

Keep actual source, generic signatures, normal/unwind/nested-Drop and ownership/leak/refinement controls. No gate exemption, guard-own=true, broad forget summary, address-only ownership bridge, checker suppression or new trusted premise is authorized. The mutable source-only chain is not part of this active chain.

## Ordered patch identities

| Order | Patch path (repository relative) | Patch SHA-256 | Translator before → after |
|---:|---|---|---|
| 1 | `research/challenge-8/overnight-s6/verifast-s6-26.10-candidate.patch` | `20f7d07ac9bdaca7c46f737b89925dfac3f4cef66c3f5d48aa9634ac949dbc1c` | `c1eb897673f88b0b8dc50798deca603bdad2c60818b6d5380ccf1dda055fe445` → `8cc9c5f6f489629e497d542a483d3c7a5ea213c053357dab915a6f0672b3c9e2` |
| 2 | `research/challenge-8/verifast-manuallydrop-new-cfg-2610.patch` | `593d09405379974ffbc475c2e0b65d648d8a6913f55b765dd0c3bebdc0922781` | `8cc9c5f6f489629e497d542a483d3c7a5ea213c053357dab915a6f0672b3c9e2` → `26af7e9e9b4f4c89614b069d0948ad67e657ac10e9cca2c21e3f70754ee80114` |
| 3 | `research/challenge-8/overnight-helper/verifast-a1-assert-inhabited-26.10.patch` | `b3fdae6588c5d88a5151f9b103b2f5ab6d2d58db880955a1b975a7f88ca2feb9` | `26af7e9e9b4f4c89614b069d0948ad67e657ac10e9cca2c21e3f70754ee80114` → `c6cdf4ff23e9a8bc3b7593f41e7f750cf2cdabd0eec8c8ada3f8b6669c9eb035` |
| 4 | `research/challenge-8/overnight-helper/verifast-a1-pointer-transmute-26.10.patch` | `44b460e64eede02bb7776ef36c6be12eb2bed2e5a4fd37ad9b733c7b5633c8ab` | `c6cdf4ff23e9a8bc3b7593f41e7f750cf2cdabd0eec8c8ada3f8b6669c9eb035` → `cf06370fc448a5ab80aad69c4b99ea0fbc613f312dae2dd120efc40559c9c86e` |
| 5 | `research/challenge-8/overnight-callback/verifast-tuple2-own-26.10.patch` | `84b58b71bfb65ac2bfac1a63d181239001cf0a7ffba3f8bfb5d5b0f1d3a640da` | `cf06370fc448a5ab80aad69c4b99ea0fbc613f312dae2dd120efc40559c9c86e` → `cf06370fc448a5ab80aad69c4b99ea0fbc613f312dae2dd120efc40559c9c86e` |
| 6 | `research/challenge-8/overnight-helper/verifast-a1-transmute-linkage-26.10.patch` | `40fb77888c9b907f150d32f9d85769512cad9c57bb0b14f9c9dbd593fc44c0e7` | `cf06370fc448a5ab80aad69c4b99ea0fbc613f312dae2dd120efc40559c9c86e` → `9eb7ae14c481482d98a5334ba8a5b725e5443c3f1760d0d352b4827035238fcc` |
| 7 | `research/challenge-8/overnight-guard/verifast-h2a-generic-guard-link-26.10.patch` | `4a36239b68dade6aa486e4bccedf77e92f4104278456d1c568c58d28efa18a7a` | `9eb7ae14c481482d98a5334ba8a5b725e5443c3f1760d0d352b4827035238fcc` → `4c1c292ce8adea0acd4feabce1bbf0d7567419dddfb863859fbb5717ecdc8d05` |
| 8 | `research/challenge-8/overnight-callback/verifast-callback-unwind-26.10.patch` | `61d7525cc8ff3e6e9c736ea00178c002f071b521c78845bf68d0e4890e2be07a` | `4c1c292ce8adea0acd4feabce1bbf0d7567419dddfb863859fbb5717ecdc8d05` → `de178e058321a384559ea0ba74f41d1f4a164976ad44a53d9ce1bee989d6b322` |
| 9 | `research/challenge-8/overnight-guard/verifast-h2b-nominal-drop-template-26.10.patch` | `c9afb4bfd696efc38f2bc71e10463a34170d9d769e851a07388c01278e99b2ff` | `de178e058321a384559ea0ba74f41d1f4a164976ad44a53d9ce1bee989d6b322` → `2472f5ecfb65ba01ffb934f6cf9ef94f77380ca396b444413ad5c92181319535` |
| 10 | `research/challenge-8/overnight-guard/verifast-h2c-guard-source-admission-26.10.patch` | `57b58e37b04c9d68aa930a6fca5a6637f5c7fe72d06cb4e8955918745f5701d7` | `2472f5ecfb65ba01ffb934f6cf9ef94f77380ca396b444413ad5c92181319535` → `9107533770badbcac739210399068c18ab8b5f013c3611f32f3ab8b71f1f1713` |
| 11 | `research/challenge-8/overnight-helper/verifast-g1-checked-forget-call-cfg-26.10.patch` | `f402a7723b9b28e97d57254fd150f398f415f5d8076c315b3508958a86b7a9cd` | `9107533770badbcac739210399068c18ab8b5f013c3611f32f3ab8b71f1f1713` → `99360de7ab92de15d28039338a0205d39bb2187bbb254f3d366dd57d21063e3a` |
| 12 | `research/challenge-8/overnight-callback/verifast-fnmut-hrtb-26.10.patch` | `cff0d5ab1798227c39029a5c18d06619ce7eece928be85f4b1c9f440307f5ece` | `99360de7ab92de15d28039338a0205d39bb2187bbb254f3d366dd57d21063e3a` → `6abe2aa920dfe9cc193d1331d0ee5e90310f2ac7609b03d92f3000959d5115bf` |
| 13 | `research/challenge-8/overnight-helper/verifast-actual-owner-fingerprint-probe-26.10.patch` | `355eaa781d9857226f57fa32b03dc6725eb61196ac4e01d63c1c6e97c5653b5b` | `6abe2aa920dfe9cc193d1331d0ee5e90310f2ac7609b03d92f3000959d5115bf` → `e88a114bee03c55291ba637449637e8da6c08f4be3ee93e4e178ad9f2d68c1d9` |
| 14 | `research/challenge-8/overnight-helper/verifast-actual-owner-admission-26.10.patch` | `f5e2c0735dcb02856a9e10e93d6b1e19095a96505058ffccf33c6bdc28e8bc80` | `e88a114bee03c55291ba637449637e8da6c08f4be3ee93e4e178ad9f2d68c1d9` → `c66a3f4aa903f4effa66ff091c3a6ea25bc8b7284f8d5cda6f6a70c8f68a7566` |
| 15 | `research/challenge-8/overnight-helper/verifast-actual-nested-ghost-scope-26.10.patch` | `11cdb0da938ed277a542181dcee5ba939b4c8b2bf15f957c389313115aeed694` | `c66a3f4aa903f4effa66ff091c3a6ea25bc8b7284f8d5cda6f6a70c8f68a7566` → `e441c283fe4d8b0faf97c9de4a38c935a21c4cf6bf8b2a4102d8eb957f39f8e0` |
| 16 | `research/challenge-8/overnight-guard-actual/verifast-nested-unit-fingerprint-probe-26.10.patch` | `cfc6b057af14cb611f9984f4eb6ee0398e3d844acaecce56f85070c42884892c` | `e441c283fe4d8b0faf97c9de4a38c935a21c4cf6bf8b2a4102d8eb957f39f8e0` → `afe841ec998c081fa237d9dfeb914f2d9111eb1c689cb27bbac51046564246ff` |
| 17 | `research/challenge-8/overnight-helper/verifast-actual-owner-nine-admission-26.10.patch` | `bafb47128b7dd9e8c84cd3492a609f00bbac193759492524b12cda7ba54effcb` | `afe841ec998c081fa237d9dfeb914f2d9111eb1c689cb27bbac51046564246ff` → `18e2463820a25084cdfe17f8a51393f09bb0341b29a4ef524a53107952993cdf` |
| 18 | `research/challenge-8/overnight-helper/verifast-actual-nested-h2-26.10.patch` | `07cc53e0823ae67ac6d53eb4e3add7bf7900261d3eb4528d6b20c3c1143bc0e1` | `18e2463820a25084cdfe17f8a51393f09bb0341b29a4ef524a53107952993cdf` → `f6f133e5e3a9eec1ca2b684f29581e833f5329bc1a79b42c88629cb759d75768` |
| 19 | `research/challenge-8/overnight-helper/verifast-actual-nine-safe-forget-owned-26.10.patch` | `7cfa66625fdb6af94162e542b078c0a08ff07bac472a5d9643fea2d153842c44` | `f6f133e5e3a9eec1ca2b684f29581e833f5329bc1a79b42c88629cb759d75768` → `071fc177b8ee69bca27c8627f44914df7f1dc8c6f2cf99a45098c32bd88d8eb1` |
| 20 | `research/challenge-8/overnight-assume-actual/verifast-actual-nine-a1-26.10.patch` | `a597d99a23895e02308f1f813c604a7dbc8235dbc3e04f3b08112087f6a572d4` | `071fc177b8ee69bca27c8627f44914df7f1dc8c6f2cf99a45098c32bd88d8eb1` → `737e16e333f0bb22a04983bbc2be0ba54d0dca6faa69eefa0a2a99781c2ec9ef` |
| 21 | `research/challenge-8/overnight-assume-actual/verifast-o26-owner-guard-literal-refresh-26.10.patch` | `0a6ac67c31b785acd5b2ab5eb9eb0158e0b5603dafda05033b7c58a6ef941c54` | `737e16e333f0bb22a04983bbc2be0ba54d0dca6faa69eefa0a2a99781c2ec9ef` → `a522a1b6f9509c16654aaa5a81ac2b939a518fc0c414464e6380a9d94400c91d` |
| 22 | `research/challenge-8/overnight-assume-actual/verifast-o26-a1-guard-literal-refresh-26.10.patch` | `ad8aa43b85a58fa4b8894fed36816aba89a9abfb0f9b80cd9547e4454ff6fb75` | `a522a1b6f9509c16654aaa5a81ac2b939a518fc0c414464e6380a9d94400c91d` → `0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a` |
| 23 | `research/challenge-8/overnight-assume-actual/verifast-r21-final-select-branch-selected-26.10.patch` | `78079210a5548fee87e200996920bfb012bcb0cd17b0b574eb926806a46e7ab6` | `0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a` → `606235c66c76412d2fdcef5f30436c342771ad5a087b343f618cfb7c8a2344d2` |
| 24 | `research/challenge-8/overnight-assume-actual/verifast-r23-fractional-forget-26.10.patch` | `f954fb593665b71b2042d9e1476fbc0d1b8de124861fb8f48aed4be8d791d084` | `606235c66c76412d2fdcef5f30436c342771ad5a087b343f618cfb7c8a2344d2` → `2d6f1950bd95b655560c767c54af8facfecde724f29a72c4218b65b6c6438c19` |
| 25 | `research/challenge-8/overnight-assume-actual/verifast-r23-fractional-mir-layout-26.10.patch` | `68810eb486d494cb49e158a13eab55b19464fad1b724bd9025cf5960b6c5bc17` | `2d6f1950bd95b655560c767c54af8facfecde724f29a72c4218b65b6c6438c19` → `cadaa80ab55e6fb3f53ccfcae1ab05dc953a2cb69a17616654d49dad6350478f` |
| 26 | `research/challenge-8/task-history/select-callee-r23/ghost-cleanup-successor-fractional.patch` | `03f91fb5fe7cb25deabe5d6d7ab4e224e5559823b0c88b75a3c717dba088567d` | `cadaa80ab55e6fb3f53ccfcae1ab05dc953a2cb69a17616654d49dad6350478f` → `103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44` |
| 27 | `research/challenge-8/overnight-assume-actual/verifast-r22-coef-typepred-parser-26.10.patch` | `dfdaff604314ecf0e27c44320811096f05a8bd8833910c59321fdec33de7b0e5` | `103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44` → `103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44` |
| 28 | `research/challenge-8/cloud-build/sort4-caller-entry-native/merge-fractions-ast-dump-r15.patch` | `f08f1c391aa62e6cbeb0ad80e73958b1b6dcfd38f40b3d7d87802d12c4a534ba` | `103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44` → `103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44` |

Row 28 applies after row 27 only when the exact R24 session enables the positive AST diagnostic. It serializes the existing `MergeFractionsStmt(l,e)` constructor and both fields, without changing the AST or verifier. Source `src/frontend/ocaml_expr_of_ast.ml`: base `898203bf8fe5802478fdfd41456b49ad07f1e6fedf0535c3d303d4ec2081c9ff`, final `f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94`. Manifest `research/challenge-8/cloud-build/sort4-caller-entry-native/MERGE-FRACTIONS-AST-DUMP-R15-MANIFEST.json`, SHA-256 `c529a3a45dc78a3f6f914d55f4e2e6cca29b7383f69827db1e20904d2db4b43b`. The R24 runner candidate checks and reports that printer hash; the R24 final source-file inventory must equal the frozen three modified files plus this utility. No R15 credit transfers.

The maintainer may use this published chain for tool integration review/regressions; proof work, acceptance and Select pins remain owned by Select. No integration, deployment or upstream publication is performed here.


29. `task-history/select-callee-r24/checked-pointer-outcomes-r24.patch`
    SHA256 `81c5e18b5f754298aae94940a98a8fa3495b9d73b179d2697493b1c704070ddc`;
    translator `103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44`
    → `6a710d26c41d69accd17aeb637e719ce7eabc321990d465a6d956ca0d0d7d93c`.
    Applied after row28, before console build, only on exact R24 runner route.
    Default-off checked-result projection of the two certified const-pointer calls;
    flag enabled only for ordinary proof variants, never fingerprint or baseline AST.
    All ten raw MIR cleanup edges and admission remain. No checker/source/spec change.
    Two patch/hash reproduction checks and four real callback-scope tests pass; UNBUILT, unproved.
    No proof credit or maintainer adoption claimed.

Row28 hosted update: Build `0d214997-138c-41ea-abcf-b337cffb8c72` reports
serializer check/apply exit0 and complete structural AST artifact SHA256
`50ae0cf9953864422f3ccc589b45045db6387d6ae90ac301205d505277b5757e`.
The Build remains FAILURE; diagnostic log reports the same three dead-code sites.
This establishes source-reported diagnostic availability, not parser-input identity,
causal proof, actual acceptance, or independent proof credit.


30. `task-history/select-callee-r24/checked-pointer-outcomes-scope-r24.patch`
    SHA256 `3f342a74bd855cc4dd4e8e639fbd6d96790d14c76e718fed1b475e673a275563`;
    translator `6a710d26c41d69accd17aeb637e719ce7eabc321990d465a6d956ca0d0d7d93c`
    → `e3c99165c2e5fc8ef5700dbaa3885c81310d26868e5e5ca61ecb019c4205d5db`.
    Same closed R24 gate, after row29, before compile. One identifier correction:
    the early admission module uses enclosing `Args.ignore_unwind_paths`;
    `TranslatorArgs` aliases the same functor argument later in the file and
    is out of scope at this point. No guard, source/MIR, checker, spec, control,
    result projection or callee-body proof change. Static application PASS;
    UNBUILT, unproved. No upstream adoption or proof credit claimed.

Row29 Build `0b240663-a082-41e9-a3e2-19a0b8738958` FAILURE: Brief reports
console-build exit2, `Unbound module TranslatorArgs` at1124. Check/apply exit0
records establish patch application only; actual projection/proof not established.
Failed candidate2aba4276 and original row29 patch/pins are preserved unchanged.


31. `task-history/select-callee-r24/checked-pointer-outcomes-nine-gate-r24.patch`
    SHA256 `90ad23d24b3806690887e396cb2ec4b10e25ae53df8115cba00649aa26889a3a`;
    translator `e3c99165c2e5fc8ef5700dbaa3885c81310d26868e5e5ca61ecb019c4205d5db`
    → `c8f5ce1da4f88a4b029b8ed12cc7667a0e227836b1843a1590f78769e073201e`.
    Same closed R24 route after row30. Require certified A1Nine active and
    independent two-body A1Link inactive/locator absent; nine certificate
    already checks both A1 local interfaces and graph before setting active.
    All ordinary same-unit callee proofs remain. No source/MIR/checker/spec,
    projection matcher/counters or normal/unwind/control changes. Static
    application PASS; UNBUILT, unproved, zero credit.

Row30 Build `bba86d46-3d8f-4275-a7ad-bd36328f4127` reports console-build exit0,
but ordinary positive RAN/exit2 with new gate refusal after A1Nine admission.
The original gate incorrectly required mutually exclusive two/nine-body flags.
No projection execution or formal callee acceptance established by that Build.


Row31 hosted update: Build `85c88d85-0bac-4f7f-8186-93a8b079b162`, proof6e62d359,
reports console-build exit0 and ordinary positive RAN/exit0. Exact log54 reports
pointer_drop=1/assume_init=1; log704 reports0errors/142statements. Positive row
COMPLETE/POSITIVE_VERIFIED_SOURCE_REPORTED, oldgates/source intact and pre/post
capture checks complete. Actual profile reports translatorc8f5ce1d, parser6a,
printerf32 and tool lib.rsspec d33b2a7a. These are source-reported CI observations,
not independent B1/B2 credit or callee acceptance. Full7-control matrix remains
unqualified pending exact target pins and classifier prior/current repair.

## Separate UNBUILT mutable candidate (not part of hosted chain)

`mutable-certificates-r24.patch` SHA-256 `e1b5b8aa78e905884565e16318e29559050e2fba41366a60d61ebdbe1aeb9099` applies after row31/C8. Generated final translator SHA-256 `eca440a605ab3900c39d9e58328b487104a1b33f75d90323036f6beab09aa162`. Closed R24 mutable case/root selector, separate predicates/certifiers/translation state; const profile retained. Independent review pending; no actual compile/proof or P2 publication. Generators and scope: [MUTABLE-NATIVE-CANDIDATE.md](MUTABLE-NATIVE-CANDIDATE.md).

## Incremental mutable A1 primitive candidate — UNBUILT

Row33 `mutable-a1-primitives-r24.patch` SHA-256 `e81f3a4c64df13432cbcdb9287a7247bd1e87884a6a35c901eefd0d7e0efbc4d`, base translator `eca440a605ab3900c39d9e58328b487104a1b33f75d90323036f6beab09aa162`, final `11d4a092b3d91570307779cfc1e5b46ff37525343a62abb162109bfedbc22d0f`. Applies only inside exact mutable positive mode after row32. New closed typed mutable A1 arms for assert_inhabited and checked MaybeUninit-pointer transmute; counters1/1; old const arms retained. Row32 compiled on Build4509, whose mutable translation stops at const-only assert_inhabited. No mutable body proof/publication/credit. Review/Cloud for row33 pending.

## Incremental mutable checked-successor candidate — UNBUILT

Row34 `mutable-checked-successors-r24.patch` SHA-256 `07eed4b28d098812bb5e263297bac08c7dc372bc707be95f3d2b01c5832275a1`, base `11d4a092b3d91570307779cfc1e5b46ff37525343a62abb162109bfedbc22d0f`, final `8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007`. Applies after row33 under existing exact mutable positive mode. Add the two already-checked mutable projection booleans to existing FnCallResult/Goto successor filter. No rawMIR/checker/gate/source/model change. Row33 compiled and A1 counts1/1 observed on489c, which fails with3deadcode lines. Row34 review/Cloud pending; no mutable acceptance or credit.

## Row34 qualification update (source report only)

Build `cb6ab304-085f-41e3-9f0a-a5cd3d0a4147` at993dd9e reports console0, full const auditcomplete and mutablepositive exit0/142statements/native1/sourceintact; root auditcomplete. Actual translator `8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007`, console `01eaa29335277643e2c16dd35b561e2aecee867fbdd64cf13b8eb1d082602cd6`. See `P2-MUT-POSITIVE-EVIDENCE.json` and bounded S15 receipts. PlatformFAILURE preserved. Mutable fullmatrix/refusals and publication pending; independentcredit0.

## Separate W4 native fingerprint overlay — UNBUILT

Row35 is diagnostic-only in a separate copied Cloud tool. Patch
`cloud-build/sort4-caller-entry-native/w4-native-fingerprint-r24.patch`
SHA-256 `e720c48a5daf9e402ceb0dfddb0b5fcbc9405bedd0f9cf7eff061e5a672dcd90`
applies after row34/`8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007`,
producing `5170c56386f092d55a42251594eb4b080073f58828cbe1dcf44053b5bdc99942`.
The closed R24 W4 fingerprint mode requires the exact source and single
`sort4_stable` body, writes native unit/body Marshal snapshots, then always
refuses before proof admission. No callback gate or proof rule changes.
Frozen capture and published P2 remain on the qualified row34 tool.
See [W4-NATIVE-FINGERPRINT-MANIFEST.json](W4-NATIVE-FINGERPRINT-MANIFEST.json).

### Row35 native input observation (not proof qualification)

Build `ddfcd255-0f99-4876-8465-e6ee9af8dced` reports the refusal-only native
probe complete, console SHA `33b693fa92790864db503fa69657e572fd2699350e6c7e1b4b2ffc3998108fe0`,
unit Marshal SHA `b711429f889c6e36393272c29fcc9c4e50fe75beb2ffe2d048ffc424b4325c83`
and body SHA `067c11f2b290d462d5a203678d069abe53ceffed6362a6ba4cd47035fa81a67e`.
Overall diagnostic remains incomplete due typed-call extraction and audit
output integration. These are source-reported input identities, with zero
proof credit; published P2 remains on row34. See W4-NATIVE-FINGERPRINT-PINS.json.

Current-native prerequisite update (2026-10-24): row35 translator `5170c563` / binary `33b693fa` has a separate exact experimental const8 + checked pointer consequence/omission qualification from Build `9984b5ac-b202-4f3a-995b-5e183e76c3d3`: [W4-CONST-NATIVE-QUALIFICATION.json](W4-CONST-NATIVE-QUALIFICATION.json). Assurance is source-reported CI plus independent static profile qualification; independent B1/B2 credit remains 0. This does not qualify the eight W4 call sites or C5 body and does not transfer the published mutable P2 profile from8a/01eaa.

## Row36 W4 contract-input diagnostic — SOURCE-REPORTED COMPILED, COLLECTION INCOMPLETE

Patch `cloud-build/sort4-caller-entry-native/w4-contract-input-r24.patch` SHA-256 `6c8cb345ebc11945f5624f6468732d9f0feb38294c7c73d48b0c748d2b4e03dc` applies over exact row35 translator `5170c56386f092d55a42251594eb4b080073f58828cbe1dcf44053b5bdc99942`, producing `f83bd98b5d466314782e47ddc2d80356a0d0736b6cfc03ade59409eb01313806`. It adds a closed R24/R21 diagnostic in a separate Cloud tool copy. The current callee const8 and consequence are freshly replayed on the qualified bootstrap tool; the copied tool only parses and compares the actual callee contract with six pinned external-header cases and binds the current caller native unit/body. All cases refuse before proof. The eight typed call sites remain a source-reported navigation observation, not checked call consumption. No C5 gate, default call rule, source/model/checker, P2 profile, caller admission or independent proof credit changes. New binary identity is not known before Cloud and cannot be used as callee qualification. See `W4-CONTRACT-INPUTS-DESIGN.json` and `W4-CONTRACT-INPUT-MANIFEST.json`.

Row36 header-syntax revision: replace S33 row36 directly over row35/5170; do not apply both revisions. S33 candidate881ed4be used patch27278f4a / translator36272c89 and compiled diagnostic binaryc79dfe7e, then rejected the positive RSSPEC at line5 because its final parameter had a trailingcomma. Current revision removes only that comma and refreshes closed header/hash/size literals. No parser, contract body, ABI type, default rule or checker change. S34 compiled this revision (binary9176c224) and reported actual/imported AST hash0671d1da equal and exact callerbody067c inputs matched; collection rejected the native refusalexit2 against wrong expected1. Native sourcef83/patch6c8 remain byte-identical in the next driver/mode exit2 correction; no callee qualification or callerproof credit transfers. Historical source/report remains bound to881ed4be; see W4-CONTRACT-HEADER-PARSE-OBSERVATIONS.json and W4-CONTRACT-HEADER-SYNTAX-DESIGN.json.

Native exit protocol metadata revision: all six mode expected_results now require exactly2; driver run/audit require RAN plus integer2 and all existing exact markers/facts/physical checks. Other exits including1 remain refused. This revises generator/manifest metadata and driver/mode hashes only; translatorf83 and patch6c8 are unchanged. See W4-CONTRACT-NATIVE-EXIT-OBSERVATIONS.json and W4-CONTRACT-NATIVE-EXIT-DESIGN.json.

Row36 collection update: Build `fffd29e2-c835-4b5b-b7be-d7236451afcb`
at `0ac30a23e0ccb4cf0f2e391d859591388b1c6ab7` reports all six input
cases and physical audits complete; platform FAILURE is preserved. The nine
measured files are recorded in
[W4-CONTRACT-F83-TOOL-IDENTITY.json](W4-CONTRACT-F83-TOOL-IDENTITY.json),
including diagnostic binary
`9176c2244f90482264d52ab30cfedd61248e6e3b0b0126eaf57e1d8310c868cb`.
This is source-reported input congruence, with no call consumption, C5 body
admission, or callee qualification on that binary.

## Row37 control-source data probe — UNBUILT

In another separate Cloud copy, patch
`cloud-build/sort4-caller-entry-native/w4-control-fingerprint-r24.patch`
SHA-256 `22a1275f4b2a0f2b52b1d9febb7ceb9e0a70655b6e1bc24118f9de0e96c12c99`
applies after row36/F83, producing translator
`1276f006b5dd757a9dc9fbf87e4d9491758c24f71ba5dc409f0c08720a528a13`.
The exact R24/R21/profile/Cloud/lane opt-in captures a single
`sort4_stable` decoded unit/body and then unconditionally refuses before body
translation. A controller-declared current fixture SHA is a data-capture
check, never a proof whitelist. The default route is inactive; partial or
unknown data-mode environment keys refuse.

The first selected batch is 8 of 37 count-five source variants. Completion
means those selected inputs were captured and audited; the full control
universe, intended scope-validator failures, checked eight-call consumption,
and C5 body proof remain open. The new binary is a measured diagnostic
output, not a qualified proof tool. No current const8, consequence, C6,
P2 metadata, source/runtime, model, or checker gate is removed. See
[W4-CONTROL-FINGERPRINT-MANIFEST.json](W4-CONTROL-FINGERPRINT-MANIFEST.json)
and [W4-CHECKED-CALLER-ADMISSION-DESIGN.json](W4-CHECKED-CALLER-ADMISSION-DESIGN.json).

Row37 S37 data update: Build `8cbcdb44-56f3-4464-9d8b-0f49b8ac164d` reports all selected8 source/unit/body captures andphysicalaudit complete, runner0; platformFAILURE preserved. Translator1276 andbinary `ee6758eafcae52664b33c523e34df0376fcb3253f0461713c8559406e8ce4a2a` measured in W4-CONTROL-DATA-TOOL-IDENTITY.json. Positive source/unit/body matchthe previous E3/B711/067c inputs. This isdata-only identity, notcalleequalification orcaller/C5 proof. Nextbatch selectsremainingindices8..36 andpinsall9 outputfiles tothese exactidentities; perBuilduniverse_complete remainsfalse.

S38 `3c2e23ad-0afd-452b-ade8-ad2947756979`: selected29 inputs and physical audit complete as source-reported on unchanged native1276/bin ee6758. S37+S38 aggregate covers all37 input fingerprints only (`W4-CONTROL-DATA-ALL37-INPUTS.json`); no callee qualification, checked caller/C5 proof or independent credit. Platform FAILURE preserved; runner exit0.

Dormant W4 native candidate (UNBUILT, no caller activation): `cloud-build/sort4-caller-entry-native/w4-dormant-native-r24.patch` SHA-256 `96ace30b1462c9bd48d7e84f6e921aac9a5d41651dc927d96f561ab216a5256c`, base F83 `f83bd98b5d466314782e47ddc2d80356a0d0736b6cfc03ade59409eb01313806` → `95c825f847bc7f5a843f4d71a8ffd10f58f7005aca1bc90aa996e0fdf7edf65d`. Includes selective C1/R16/R17 five-index scope/deferred/CFG machinery, source-only37 input table and ordinary eight-call/header-consumption guards. Existing R24 checked-outcome/mutable A1 paths retained; Caller.active defaultfalse with no enabling assignment. First Build only compiles and measures nine-file identity after retained const8/consequence/C6/source29 checks; no new-tool callee qualification, W4 proof, P2 change or independent credit. Exact authoring dependencies in W4-DORMANT-NATIVE-MANIFEST.json.

Dormant candidate d6f21439 rejected before Cloud (R24-w4-dormant-compile-review.json): old undefined diagnostic flags; audit scalar type gap. Fixed dormant source `758acf141b9913b1f418482b1afbd78e8cf11ecbbcb21ed65df8bbb8d45eef5b`, patch `bd963870ff5a136040b0f40121a5fabe66db9db6107d7b7de2954d93b1aca344`; still UNBUILT, no activation/admission/qualification/credit.

S39 `7ef645ef-9d1a-42bb-af6a-023e214e9aca` stopped in new controller prerequisite validation: nonexistent caller_body_proof_admission demanded from const-consequence producer. Brief reports empty new stage/command inventories and null new binary. Native758acf remains UNBUILT; source-only input universe unchanged. Controller fix follows actual per-producer schema; no qualification/admission/credit.
