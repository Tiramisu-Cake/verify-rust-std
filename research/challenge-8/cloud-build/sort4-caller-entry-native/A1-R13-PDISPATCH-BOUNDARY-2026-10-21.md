# R13 P-dispatch source-boundary record

## Finding

The R12 S4 diagnostic reached translated-call verification with exit 0, but its
P-dispatch classifier remained `INCONCLUSIVE_DISPATCH_OBSERVATION` because the
source-derived caller call inventory differed. The first deterministic mismatch
is order within `quicksort`: the source and AST inventory is threshold call then
`small_sort`; the old collector sorted the rows by callee name and emitted
`small_sort` before `small_sort_threshold`. The collector's exact call-set,
generic/argument checks, and downstream owner/callee bijection remain required;
the ordering fix does not replace them with a count.

The required three-entry order is:

1. `quicksort` → `StableSmallSortTypeImpl::small_sort_threshold`, source line 166.
2. `quicksort` → `StableSmallSortTypeImpl::small_sort`, source line 167.
3. `a1_guard_observer` → `StableSmallSortTypeImpl::small_sort_threshold`, source line 142.

The corresponding source call intervals and separately reported AST/MIR spans
are below. AST columns are the `proof-ast.ml` one-based source coordinates;
MIR columns are the `normal-mir.txt` zero-based `callSpan` coordinates. Preserve
each range separately: AST and MIR spans are compared to their own records and
are not required to be textually equal.

| Order | Owner / callee | Source line | AST call span | MIR call span |
|---|---|---:|---|---|
| 1 | `quicksort` / `StableSmallSortTypeImpl::small_sort_threshold` | 166 | `verified/lib.rs(166,19-44)` | `verified/lib.rs(166,18-43)` |
| 2 | `quicksort` / `StableSmallSortTypeImpl::small_sort` | 167 | `verified/lib.rs(167,13-47)` | `verified/lib.rs(167,12-46)` |
| 3 | `a1_guard_observer` / `StableSmallSortTypeImpl::small_sort_threshold` | 142 | `verified/lib.rs(142,19-44)` | `verified/lib.rs(142,18-43)` |

Source call lines are from the exact archived generated `P-dispatch.rs`. AST
call locations appear in the exact archived `proof-ast.ml` under the respective
function definitions. MIR `callSpan` source coordinates appear in the exact
archived normal MIR text. These retained coordinates support the intended
order and candidate ranges, but the archived classifier did not successfully
join the records into a three-row P-dispatch receipt. Do not represent the
candidate spans as a successfully established AST↔MIR/parser-input binding.

## Evidence identities and bounded requests

Build `fbc0834a-760b-4f56-98fe-952714f36c6d` has archive SHA-256
`a6ef54e1cdca03379d602c7fb01fd2834512ee3bd1e5362be72704374a387591` and index
SHA-256 `bb237a6f2228cc0f7f486df05a330e31b27299f77868cbd3d6e87376d1bc458b`.
The Brief reports `VERIFIED_ARCHIVE_AND_INVENTORY`, source-reported run exit 124,
and `NOT_ACCEPTED_AS_REPORTED`. These are delivery/verdict claims, not proof.

| Retained member | Catalogue file ID | SHA-256 | Exact bounded request IDs used |
|---|---|---|---|
| `allprooflogs/cases/sort4-c1-current-recovery/focus/P-dispatch/dispatch-join-observation.json` | `ba8f2c2c1d9881a69e3ace3ce18a4c2be31674d5b1fc6ddd5fcf694f7b6f7746` | `07a35ecda4a50f8fcd6164b1aaff505fa25864fa3410cde9662faa307cc059dc` | catalogue/search `dispatch-join-observation`: index `bb237a6f2228cc0f7f486df05a330e31b27299f77868cbd3d6e87376d1bc458b`; info `6ba7ca7f38f3836661d19febd6223e4554fc1e6ca2049bd53fbb097be13a1531`; root children `5ffa67d3e27a875a0ebe7851a39f9717be8d6f00efec3e0e6a020eef3c6f75a7`; `/dispatch_classifier` `7a8812e3edd40e24a1c666fe9a74efd81a8e2682d691f817965009a2cb24c543`; `/source_pair_sha256` `878d9da5ed05059c25250103a79edd855cf94b8dcd4bd46f84e2ed765e5bcae2` |
| `allprooflogs/cases/sort4-c1-current-recovery/focus/P-dispatch/a1-focus-raw-observation.json` | `7f75e04286ce5b8ef52b56a7b6a82ce7ad4a1ccc43f4c32d29e0ec1eaa113a2f` | `7a8a40427c36dd0a60727ecd32574f4556ccacc308d1fc7fa346f114615248b9` | info `3f9c093db262cf6bffe5e379bc3c30f19d7c11d91c1d0379cbccd8b07061fdb3`; root page 0 `00eb0033de1d040fac7ba00ee9d00ac87de1e5b6ae64ad28611def576ef8a5f2`, page 20 `80cf8823539273b004502b62800812895d5dc42c51fe05714c020e51cb515ec4`; `/source_pair_sha256` `1ddd0c85fee50e990538e7f502c059b56a17fd6a16ab656c12b8036326ed2c25`; `/paired_support` `090837901d6155900db47404303e267ba7ef062be0f3efd8d0cd4443e551baf0`; `/paired_support/full_mir` `7a0e500f86ebd004fc4be2c370caedf94bc2dcfc10ef4dd3a3ac44c33c2eb727`; normal full-MIR row `f93122f4ab5ae8bfe7e9b0d37cb5a83ba88cec173ec4adf6f32649c0e7daafd2`; readonly full-MIR row `aa5be17ea07b57ed7a5f5ecb1465fee3711dcbdc3c225917bc0a4291ca08c19a`; `/stages/verification` `94b5c56b6ecbda716500c6f2beeec5f98ad5df57ab5b12c78024b770d3eaccc9` |
| `allprooflogs/cases/sort4-c1-current-recovery/a1-source-package/P-dispatch.rs` | `640a3bfe094c17b9482651a78de6c7638aa64cbb647c5484969ea00404b444fb` | `0d9921640d286480bd74fc52602363eff002d8fe7400640c2e781a07def45ca5` | info `2d494686d8d975a2a0772224f9cf4b50f8508985fb131e7757d030c640f3b434`; threshold locator `7467216dbab9861782310cb02ab165860f2aeb72d3fb350074ee523ce2e65df6`; `small_sort` locator `a0992321e89124250b6e101fef51304fb46eeffa3f5a9958dc084726aaca8bb8`; lines 20–31 `7c9d7610cadb10734a38977ac22d7f7e6f16dbad994dc7a89f77bd6a9d731fa9`; lines 136–147 `2931a3918b56dbf6caddbb0d433884eaa4e5abee44d2126a418a85c6ad06c428`; lines 154–165 `7cf4c86afd8789b88afff237ee390c5dcd1919783b662514c910800a0dca814d` |
| `allprooflogs/cases/sort4-c1-current-recovery/focus/P-dispatch/proof-ast.ml` | `dda7055225217074557b0f1123c24d9e7b5f626c1fe08d02854547c092be119d` | `c693b16420a25a2607c63e194ee8dc47383a6489d08276a766252c5b87cabddb` | owner locator `819af13357c5104cf74ac1e46e80020aa18077e55db24bf4a8559d09e9fc4d18`; threshold-callee locator `02f53c5574bac2552ee52cf132fe5814742a72404986109ddb447702591e6952`; `small_sort` locator `d408cbfd2cd5eaaf356bea433e2a606efea6335b9ed8e382802780518ac1b88f`; observer lines 682–690 `6d7f52e06d9efa2173463535afb9231af3ac78110c30d38c3ce8b43de6f5ff2`; quicksort lines 812–823 `6a7f89138ba01f038809c7d23a26d0e31363d974dd4fdc96dd61b776b984bcc4`; quicksort lines 824–835 `c1df355659792dca28f9f505bd116a6eda496240e90d9edb8c13ee5c1bcf5fc7` |
| `allprooflogs/cases/sort4-c1-current-recovery/focus/P-dispatch/normal-mir.txt` | `43410253827795265d7cc189b1e4bd6adaa6f360b342960617480439ab96516a` | `f2deb3162a7888409af40bd5afed5c0c8c3deb7e5abc5d349d7033acdc05b845` | info `2f6be603f10c74c7963dd566c39740f479f653348b9cd4110633e3a537fcbb27`; owner locator `b1bac25a265892de95e9ce9a00a9a13d13239b31121dcf2f0b07d241e762d083`; observer MIR span windows `f8e95c18e4ab9ee080cde85562d7358203feb54a08403106ea80c8f50d6585cf`, `71301ffcfe20453deeb1ffb2a1eac2c8c136b44e18d3974e7f8078cb3b53db78`; quicksort MIR span windows `27acd8a04b14b49aa8f4bca0108cc827ce051d263280271687e6d14f87a62484`, `26ae150970d43cfc86f115ddd4d7c05181751c9f0cf31561305cf030ae6a8206`, `724c66d118425557aaee1396bdec843b37ae7c5796e3fc218202d0e7e1ced224`, `1a6288d4f89375475ea5fd0e5e5f70c6add81b920ad25527431f8091cfcad52` |
| `allprooflogs/cases/sort4-c1-current-recovery/focus/P-dispatch/readonly-mir.txt` | `bf4ca644bbbba76227694635ec53af3bc6da9fb37552d659f5a9a3d5f44c850d` | `680291e3630891a3d882bf8c88f15a91aba6d32853a524ddc73ad7f1c3275cc2` | catalogue entry: `P-dispatch` search; retained size 465738 bytes, sanitized projection coverage is partial |

Identity values in the raw observation: Build ID `fbc0834a-760b-4f56-98fe-952714f36c6d`; profile SHA-256
`dcc4707f2913a876c53536f79cb85da15380634712ffb083f88dcdb8737a77cf`; source ID
`925312cd19cb71d0c61a10eb179e13d5c0f0b711ccaef6986bc2136aba6ca6ee`; unit ID
`6bb5b4f4eccd8c07a6e6e7c45d0476b442c033f8fae7fc8bc1a1184d20a52bff`; source-pair
ID `0d9921640d286480bd74fc52602363eff002d8fe7400640c2e781a07def45ca5`; original
source SHA-256 `43238ed0c696584c97d26aa38027f5980602f081bf007791095b1bfccca2b518`;
verified source SHA-256 `0d9921640d286480bd74fc52602363eff002d8fe7400640c2e781a07def45ca5`.
The verification stage is terminal exit 0 with log SHA-256
`473dd23906cb8d912f58e7eba2fbf4ab8e9dc9dd1678711f86b4b7a17e304d46`; AST SHA-256
is `c693b16420a25a2607c63e194ee8dc47383a6489d08276a766252c5b87cabddb`.
Paired support reports `paired_support_passed=true`; normal/read-only full-MIR
members are separately identified by SHA/byte counts above. Their presence and
the paired-support flag do not bind the failed dispatch join to the parser AST.

## Boundary

The dispatch observation reports `reason="source-derived caller call inventory
differs"`, `paired_support_passed=true`, `verification.exit=0`, and
`caller_receipt=false`, `matrix_admission=false`, `proof_credit=false`. It is an
inconclusive structural observation. Evidence Brief marks
`parser_input_binding="NOT_ESTABLISHED"`; file/index/archive identities and
exact text coordinates do not establish parser-input↔AST↔MIR binding. Do not
claim that the three candidate call intervals form a successfully collected
owner/callee bijection, and do not infer proof credit from verifier exit 0 or
archive integrity. Missing/extra/duplicate/redirected/wrong-owner/wrong-span,
stale, or unbound rows must continue to fail closed.
