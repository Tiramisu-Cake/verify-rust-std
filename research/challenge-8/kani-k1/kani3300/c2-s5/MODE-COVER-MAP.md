# Mode / cover map

| Old file / root / source cover | New obligation (proposed selectors in ORACLE-MAP.json) |
| --- | --- |
| replace.rs / replace_transfer / 42,45 | Exact-base N=2 read failures + caller payload SUCCESS. Negative no covers. Initialized role => that own conditional SUCCESS; uninitialized role => separate same-mode false-partition companion N=0, postreturn SUCCESS + SATISFIED cover. Replace support UNCLAIMED. |
| replace.rs / replace_ordinary / 57,60 | N=0, useful `payload_is_42(&result)` assertion + ensures SUCCESS; both initialized return consumed / uninitialized storage returned SATISFIED. |
| replace.rs / replace_simple_check / 72,75 | Independent SimpleCheck file, same two SATISFIED source covers and useful assertion/ensures SUCCESS. |
| recursive.rs / recursive_check / 57,59 + target28,31 | Sole cycle Unsupported, N=1; pure true cover hooks may be removed in this negative copy only. Keep conditional payload assertion and original target recursion/contracts. |
| recursive.rs / recursive_ordinary / 71,73 + target28,31 | Same boundary in separate Assert file; not legal proof. |
| recursive.rs / recursive_simple_check / 85,87 + bounded40,44 | N=0, both return covers and base body reached / unrolled body edge reached SATISFIED; useful payload/ensures SUCCESS; depth0/1 and initialized/hole alternatives unchanged. |

Keep nondeterminism. An existential branch cover cannot become assert(branch).
SATISFIED generated copy counts; UNREACHABLE original copy does not. Use consecutive
function-prefix / Status: SATISFIED / Description for each unique cover; summary N=0
anchored to SUMMARY distinguishes check and cover counts.

CC4 isolated-bounded/isolated-recursive-ordinary/mixed-reversed are diagnostic inputs, not
additional exported JSON root selectors. Preserve their code/conditions in the input inventory;
only one-harness splits become expected selectors after all map blockers close.
Mixed source order is not observed producer order. See MIXED-ISOLATION-DISPOSITION.md.
Only pure cover!(true, description) hooks are removed from negative Replace/recursive copies. All payload reads and assertions remain; positive copies retain required SATISFIED covers. Six old mode roots map to seven fixtures. The new false-partition companion N=0 is source-justified, native NOT_RUN.
