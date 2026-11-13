# Worker14 control map — source-only preparation

Exact source commit: `0beeb6b79efb72b88035e2b747aa889e9b1cb4d4`, parent
`ee2695e5a2c4c2d8ead7a511e0f3f6f2a9a95677`. No production change.
All actual outcomes NOT_RUN; every emitted/source binding BINDING_PENDING.
The two roots named postcondition_reads_returned_hole are different cases/inputs.
Hashes, current lines and source-operation text are in ORACLES.json.

| Case | Input under tests/expected/uninit | Exact root | Intended complete oracle / remaining binding |
| --- | --- | --- | --- |
| p1 | closure-zst/scalar-pfc-legal.rs | postcondition_reads_initialized_return | SUCCESS, zero failures; first initialized u8 read and useful outer ensures reached SUCCESS |
| ordinary | transfer-qualification/legal-pair.rs | legal_ordinary_transfer | SUCCESS, zero failures; original ordinary body, result7 and array/out123 assertions |
| pfc | transfer-qualification/legal-pair.rs | legal_pfc_transfer | SUCCESS, zero failures; body/ensures/frame and harness result7/out123; private writes lawful |
| lawful-modifies | private-transfer-frame/lawful-modifies.rs | lawful_modifies_preserves_outside | SUCCESS, zero failures; initialized relay/choose, result29/out29/outside41, useful ensures and harness reached |
| p2 | closure-zst/scalar-pfc-hole.rs | postcondition_reads_returned_hole | Exactly two failures: local Check and delayed CheckRef of the same ensures u8 read; IDs/class/exact descriptions/types/core location/callsite not guessed |
| postcondition-hole | transfer-qualification/postcondition-hole.rs | postcondition_reads_returned_hole | Independently bind the ensures u8 read and both instrumentation layers; count/IDs intentionally unset until CI, not copied from p2 |
| frame | maybe-uninit-contract-frame/main.rs | frame_negative | Exactly one user assigns failure at original line22, *outside after legal relay/choose/new29 read; bind actual target, never any var_N or private write |
| clause | maybe-uninit-contract-clause/main.rs | clause_pfc_negative | Only requires clause_helper's u16 read at original line22; full count/IDs independently pending; reject frame/protocol/Unsupported failures |

Lawful source retains modifies(out), result29/out29 ensures, the body and all three
harness assertions. It reads initialized *outside41 into MU and writes only *out29.
`LAWFUL-COMMENT-DELTA.patch` records the entire delta from the original fe36afc4
source; only the explanatory b12 comments/flags change. Original source SHA256:
`f629b795969f197ef289061c88ebc26e08c8fe969a6f82f643897451bfbdf90f`.
Candidate hash is in INPUTS.json/ORACLES.json. No duplicate P1, carrier, aggregate
assigns or production code was imported.

Private writes must bind to the exact private main/buffer state targets allowed
by the actual frame; user *outside remains excluded. Source line/text presence is
not an emitted assignment/points-to/AST-MIR binding. Existing legal-pair capture
success is coordinator-reported evidence, so a capture alone is not Unsupported.
If lawful root actually hits a reached nonzero closure-layout Unsupported, retain
its operation/type/property and STOP; no layout/points-to/contracts/masks changes.

Every negative requires lawful prefix and the full failed property multiset.
Unreachable outer assertions after the bad-read guard are allowed on negatives;
unreachable useful positive assertions block qualification. Unreachable service
Unsupported properties are allowed; reached Unsupported or any extra failure is
rejected. Both uninit layers are preserved, never deduplicated into one property.

JSON0.1 lacks successful property identities and failed-property function fields.
The scenario therefore crosschecks complete regular counts/status/IDs and uses
selected successful regular records with full location/function. Source/GOTO
mapping and artifact SHA/selectors remain explicit reviewed external bindings;
checker acceptance alone is not independent formal proof credit.
