# Recovery recipe duplicate-path removal

Defect: selected-proof.py appears in both infra_paths and proof_paths, although the R17/R19 complete actual-body path does not execute the selected-prefix driver branch that loads it from infra. Applicability: existing recovery recipe source inventory only; no lane admission/profile/tool change.

Invariant: retain the proof-side selected-proof blob and all profile/manifest pins, legacy source/helper modules and five-call/eight-select/four-copy controls. Remove only the unused infra path. Blob bytes are already shared by source-input.py's global oid pool: this cleans an extra path reference, not a duplicate104KB blob. No claim that this alone solves192/191 transport.

Validation: generate/decode static Git-object packaging for baseline and candidate, verify selected-proof remains only in proof inventory with the same blob SHA, all other selected path records remain, and report actual encoded payload parts without dispatch. New stage-specific helper extraction is inactive and separate; no compiler/preparer/verifier is run.
