# Exact infrastructure transport for bounded Cloud recipes

The committed `o26-recovery-tests` input archive exceeds the Cloud substitution
limit because `source-input.py` currently adds every top-level Cloud Python file
to every recipe. Most of those files belong to unrelated lanes. The rejected
archive was never submitted or reserved.

The `infra_transport: exact-recipe-v1` marker selects only the fixed Cloud
transport/provider/evidence core, `run-proof.sh`, the exact recipe's committed
`infra_paths`, and that recipe JSON. The two initial recipes list each enabled
shell/Python module they execute or dynamically import; the Cloud preflight
checks a reviewed minimum dependency set for these lanes. A later marked
recipe must list and review its own complete transitive inputs. The generic
preflight checks its declared entrypoint, exact selected path set, and Git
closure; it does not infer all dependencies from arbitrary source code. The
initial recipes' `proof_paths`,
proof commit, profile pins, and verifier behavior do not change. Stock,
constructor, and unmarked recipes retain the current broad Python policy.

Both creation and restoration require a committed recipe with the exact lane,
entrypoint, sorted unique paths, and known marker. The selected Git commit,
root tree, each selected path's regular-file mode, object ID, content hash and size, and
the complete selected object closure remain checked. The restorer requires the
exact selected infra path set and byte-for-byte committed recipe equality;
missing, extra, substituted, symlink, or mismatched declared dependencies
refuse before running a recipe. An undeclared dynamic dependency cannot be
read from another source and fails at use. The archive size limit is unchanged.

Every marked research Build runs Cloud-side negative controls for a missing
declared input, an extra path, nonregular mode, altered selected-path hash, and
an incomplete selected Git-object closure. The initial lanes select a reviewed
transitive dependency for the missing-input control; a later lane selects its
mandatory entrypoint. The hash and closure controls restore corrupted copies only
inside disposable `/workspace` directories and leave the canonical restored
input untouched. Their report is transport diagnostic evidence only and cannot
count as proof acceptance. This change does not authorize a separate smoke
Build.
