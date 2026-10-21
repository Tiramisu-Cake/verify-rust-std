# R13 S2: remove duplicate unconsumed infra selections

Static pre-submit construction for candidate a5c388fea3f4d4688137c94612b13825803ba44c
refused a 571927-byte payload at the unchanged 191-source-substitution bound.
No Build was submitted and no envelope/cap is increased. The R13 execution
uses two selected Git checkouts. Its entry/authorization adapters and runtime
helpers are read from infra, while a1-runner-r13 loads the shared core from
proof, and the core loads every A1_HELPERS entry from proof/HERE. The reference
probe and normalization patch/manifest/profile are also read from proof. The
recipe had redundantly selected these files in both checkouts.

Remove only those duplicate, unconsumed infra selections; preserve their exact
proof paths and blobs. Keep all historical entry/runner adapters plus driver,
selected-runtime, selected-proof, compiler-query, ghost-strip and first-scope
audit infra dependencies. No consumed source path/content changes, no source
codec/chunk/argument/substitution cap changes, and no coordinator/backend change.
The current R13 closure must be statically restored and every selected path
compared byte-for-byte to its committed source before submit. Historical Builds
retain their original committed recipes and object closures.

The duplicate-only closure at09f2ec06f7048be8db7e3019894743c4e653c42c remains571771bytes, still over the unchanged bound. The current R13 recipe additionally omits the two unconsumed R11/R12 profile blobs from its proof selection. Their only runtime reads are the closed R11/R12 authorization routes (and corresponding dynamic profile-table entries); R13 selects its own exact profile at every entry, core, tool and focus gate. Both historical profile files and their earlier committed recipes/closures remain unchanged in Git. This current recipe is for the authorized R13 execution; it is not a retrofit of old Build inputs. Keep older baseline/experimental patch profiles actually used by reconstruction.
