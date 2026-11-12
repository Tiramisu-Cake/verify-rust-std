# Exact U → R1 runtime partition

Source path `library/kani_core/src/mem_init.rs`. U `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`; R1 `1cd96e354ec45346b61c245554a50a8af8cb5ce7`.
U blob `37b9da8d674afb814f5024a20b77350ad5f82fd8`, SHA256 `88f260ddc5b315a32e64b0f6f396451373d2fb54f1a4898233508ebd81cd993c`.
R1 blob `6f832d4c651f8770a46327beb6e4a957b06c1166`, SHA256 `d565a600e34ef6199f4c6e0a799a5eb9a224ec0ed9a563ef47da2cbbe908cc06`.
Whole full-index delta SHA256 `ae63a74ec8381e5e11f77aa2f76a4a16b9d80695a7615fe35d72a27ec5a923d8`; exact +77/-33. Compiler/emission/contract/macros/tests/driver/toolchain are outside the partition and frozen at R1.

## Header inventory

Header hash is SHA256 of the header including LF. Context hash is SHA256 of all unchanged unified-diff context payloads including LF, in order. Hunk hash includes header, changed and context lines. These are git-object source hashes, not emitted binding.

| Hunk | Exact header | Header SHA256 | Context SHA256 | Full hunk SHA256 |
| --- | --- | --- | --- | --- |
| G01 | `@@ -18,9 +18,6 @@ macro_rules! kani_mem_init {` | `58d0e265ea19cc986d9d085d07dc685fba04a8c07417d607c71590d7ae999522` | `520d99728e851b505c9a9ad917f27f26032980bca4482f0ebfd84ff750178c5f` | `d76d235f962cd5abe32a1242347cc320b7f3dd1bf7be88a16e8400e430b50b9e` |
| G02 | `@@ -38,13 +35,29 @@ struct MemoryInitializationState {` | `1ffbe7689125d2562b0791611d866691d332cbead5e51ffaf69f216b27d7ca37` | `6f5f2308dda3f9255731aee2c73e4afa6827122d7e0ea1691d9457d282ae64db` | `bb5e8b36b299f9777001ae42296f262a206af26f6e1faa66cbc1fd0a62c346f9` |
| G03 | `@@ -105,10 +118,23 @@ pub fn copy<const LAYOUT_SIZE: usize>(` | `80209dbef6ba0cb7b225ae844374651f53694ba5cc4bf032fee633429637a8dd` | `fbd1dd5139c91812123123c7620125dc673e686090508a84cac8650483f905c4` | `628d1195bb85b73789c2c6b8279acff5640b305a84453d96e54613a4f985dfba` |
| G04 | `@@ -116,12 +142,14 @@ pub fn copy<const LAYOUT_SIZE: usize>(` | `bfb5811ea27d191804d74ea1a1371e3bb21c303936e4a933267a5e22c1b9f5b2` | `c2dc3fc3c8280834fc8ab3062eeb2fff37f3bb205e2dcc8a7af16564e4c916fb` | `acf05a2f1c04a18d770279878a0d3bfb0827d88c4a326ebeaa8fcb752ad63099` |
| G05 | `@@ -131,7 +159,17 @@ pub fn copy<const LAYOUT_SIZE: usize>(` | `5dfa377014586f9a338f2848475a39a447a7155a13f4932f164da1a90d00e3e2` | `ac0748e7a422f36fb366d0a7a62dcce1c4e612bab0ee0e05f90a7e76d9037189` | `f128e1d688c24621d5a757968800a2a9724088c4d425e78102eaa12cbeb1229f` |
| G06 | `@@ -198,6 +236,7 @@ fn initialize_memory_initialization_state() {` | `3bc7683b0249ec76a66dffdbd50b6a4f63ccc5adb045389841743f87f9519f34` | `83a97a3f8859b7e3271c1d959778aea0b9bd6bd263a14e910af2e4d26fe6dd57` | `932fd60b7b6a13bf07de560204bf6a49a75191e1ee9f6def485ce3bc00788145` |
| G07 | `@@ -358,30 +397,22 @@ fn copy_init_state_single<const LAYOUT_SIZE: usize, T>(from: *const T, to: *cons` | `b47b29218c938850fb9f2c7176f8081b7fb35f901576cf7b6630824597f284e8` | `49685f6251357a6c9c65ac349f8daa5f2edd7b8456253e2756f194174c667944` | `f78d0215f929dd2658ab9477b162cd482030831167b4441247a39a2c1a98e518` |
| G08 | `@@ -394,15 +425,28 @@ fn store_argument<const LAYOUT_SIZE: usize, T>(from: *const T, selected_argument` | `c306b137fa20bb2735572cc6f398e9ce7ac8f6c01aeea8e83a1613b1e8fdf41e` | `51bfacb6d3b82cf418cb3e538fb9a79f9660e94b7701f7824edb65a7d7b213a3` | `3de04233e3f7f1d73a9cf44059a2ff57aaad6e17f3482a71df18bddb92cfb659` |

## Complete atomic change inventory

Ranges below are zero-based half-open line intervals (`[n:n]` is an insertion/deletion anchor), against exact U/R1 blobs. Atom source hash is SHA256 of `U changed bytes + NUL + R1 changed bytes`. Atom context hash is SHA256 of `U window ±3 lines + NUL + R1 window ±3 lines`; no normalization. Each non-equal opcode is assigned exactly once, including formatting; there are no uncovered executable changes. Attached comments travel with their coherent owning group and have no separate semantic claim.

| ID | Class | U lines | R1 lines | Function/type/dependency | Source SHA256 | Context SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| D01 | Hbuf | [20:23] | [20:20] | global Option<ArgumentBuffer>; store/load dependency | `8fda67e23c73b02f819a7163ae1c258361fba17562f42f3c1bba325132a65145` | `643b7ce39627c3f64252553eec6cc9dec88abd2312cbaf77e4fdb9e0880c2337` |
| D02 | Hbuf | [40:40] | [37:44] | MemoryInitializationState buffer fields; constructor/store/load/reset | `ba9be95bdbfc5c3b74c12e8bef9682a339993fb3fdf4a1ce97a0d656942c71d4` | `b211aae1f9d86e7befb554d720ef87e431679559e7b3cdaa7008c294b109c7b6` |
| D03 | Hbuf | [46:47] | [50:60] | const new(): initialize all fields | `fe1194a604aca284bc50441c637b484af2805c1c50ae26b56e94f0a56e6d7352` | `187d54ef8e06d714e3a3c05476f21db79c5acf5d5b6a67303f0c1a295832e537` |
| D04 | comment-only | [107:108] | [120:120] | blank separator in copy; no executable content | `102b51b9765a56a3e899f7cf0ee38e5251f9c503b357b330a49183eb7b155604` | `bf7f834db09dd57f157001129dd717863bbfe50d672b40447e7791b32e102c4c` |
| D05 | GLUE | [110:110] | [122:124] | pointer copy wrapper delegates five usize values to by-ID core | `85a300b81e1dceade12fb347a408338fc8f3c8594debd5c24956473e5d89e124` | `346b9d3ac188052d144b7fc3f4cfa4e4ab2a0c27426ce067fd304f984d9829e5` |
| D06 | GLUE | [111:111] | [125:137] | copy_by_id signature/attribute and attached lifetime documentation | `9e82f2fc689deac6b2c749b76b46d03bf6430d887aea988973e830df3352f6c1` | `d869a6e1deb288b2894fce4999c3f1e30eef3a9fb4fc3e87556e13f20bd0c399` |
| D07 | Hcopy | [118:119] | [144:145] | usize retarget association/order | `95923e84141127f6c35b148cb93bd20840f4bb2b8ff9951d92d51a8bf0f709a8` | `109a584f26ad5e3885dde0164f51e4fc183e4eebbe17d4d18328d1dbd50378f7` |
| D08 | Hcopy | [120:120] | [146:147] | successful retarget early return | `5dfb7cbd5512d40e3de3f978171bd0d2b06f7cdd81edef3cc9c53d73ba9de7d0` | `13e56eb0a0ff2f092ab9ff1682076caeb2d2da5747add69ab1483dd55709ffe5` |
| D09 | Hcopy | [121:123] | [148:148] | remove nonmatching-only count1 fallback | `2815b1cdd1e0605f37b3425dedd8d7b2c538d5871b1b04af9432260072ac7be5` | `d5a3c490db3ab807d584e520e9091e39dae0466f648f92ebb696e2271a105f69` |
| D10 | Hcopy | [124:124] | [149:152] | unconditional full-count tail + attached policy comment | `b441587e5f553fd8b0099e6dfa32dcb2c08c51a17ad9269a1a4fcf4ad83a466b` | `9e2463c0015836f632fc6489b9474328027ba23da6a67b77201857b0463df629` |
| D11 | GLUE | [133:133] | [161:163] | pointer bless wrapper delegates object/offset/count | `b440aa2b3485c831ff5966ccaf46953c2f7c62b4fad6d4d1129056e34c80b59c` | `b162489001a710d975b043e67d427aa46d81d3059c53281dba5134d00351572b` |
| D12 | GLUE | [134:134] | [164:172] | bless_by_id signature/attribute and attached documentation | `36d3ac038a2bbc554b6dc7c0c285c45c19abff783ad173208521c9707275fb69` | `cab60701758fea693f8cc34be8c5423c38fe218e696015ea2e1660b0ae5fb7b2` |
| D13 | Hbuf | [200:200] | [238:239] | initialize: active=false reset | `1178e9585a6d0c421927793a0549f2474990aecb2195e43fa8558f96cfa1f267` | `ce7a9dec67523aaaf28332e59f15e1b30b76093549232d6b53726849f611282e` |
| D14 | Hbuf | [360:370] | [399:399] | remove Clone+Copy ArgumentBuffer record, coupled to global Option | `e823cd0db4fccb74be862c99714817cd78613606062b0dc843ad1d11022f73e2` | `66ef21a7537ccf07761d1ab98226207298f852d9b3b94b8cc334fe9c19aa6631` |
| D15 | Hbuf | [376:378] | [405:409] | store: capture IDs/offsets and mandatory return0 choice | `e3c42572241ba52ad14b5b8f88c8598b1011f366f6858b828eed5f6b7bdf9511` | `4a58fb49c3785a07e417156dadd4ef549ab35b20ba60b403d2a48d51198700f1` |
| D16 | Hbuf | [379:384] | [410:415] | store: five scalar writes replace Some(pointer record) | `dae880de1a381db4ef9c4884b99926090ad0efe27321a4c2595dd9b84b8363de` | `5bb6f1021a3649d9fb0d2b56bb99f92bc303af0f46585aa0961df55f349d9f22` |
| D17 | Hbuf | [396:404] | [427:447] | load: active/index/layout/ID transfer+clear replaces Option pointer transfer | `7144902a3f563714a02534e992fbc625bfc13024debc588ee191b131d483358f` | `da94ac9b6ddc624ca7a3694b88c7b60cbea9ffa44724502cc500060bb1a79059` |
| D18 | Hbuf | [405:405] | [448:449] | load: move matched return with coherent consumption block | `3fe5533f108b2a668e31f6bb08cb130fff9a664150e68a7b4f1ed55a8911328d` | `efe1dd6af4008da8d3b13ed8c0c8d49378350c334353ed7e9119a44a1c817d96` |

## Coherent groups and dependency boundary

**Hbuf**: D01–D03,D13–D18. This is representation, constructor, epoch reset and both capture/consume sides together. U restores separate **unmarked** `ARGUMENT_BUFFER:Option<ArgumentBuffer>`, with `selected_argument:usize`, `saved_address:*const ()`, `layout_size:usize`, Clone+Copy. R1 removes it and puts active:bool plus four usize fields in the marked main state. U has no buffer reset at initialize (global initializer None only); R1 resets active each epoch and clears it only on a matching consumed load. Both mismatched loads retain buffer content and bless one element. A declined U store can leave stale buffer content. Mandatory return0, pointer lifetime and frame losses travel with Hbuf, never silently repaired.

**Hcopy**: D07–D10, transition core and its blessing policy. Range guard `from_offset+num_elts*N` is textually unchanged; arithmetic types and actual widths still require audit. R1 relative retarget+early return/unconditional count-num_elts tail versus U legacy `k += to-from`, no early return, matched/declined no blessing, nonmatching count1. These are one dependency-complete policy group, wider than separate R4 B or C.

**GLUE**: D05–D06,D11–D12; D04 is whitespace-only attached to the copy split. `copy<N>(&mut Self,*const u8,*const u8,usize)` captures two IDs/two offsets then calls `copy_by_id<N>(&mut Self,usize,usize,usize,usize,usize)`. `bless<N>(&mut Self,*const u8,usize)` captures ID/offset then calls `bless_by_id<N>(&mut Self,usize,usize,usize)`. Signatures, pointer-check attributes and thin wrappers remain exact R1 in **both candidates**. Range/bless core is the same predicate after parameter extraction. No ID→pointer reconstruction. R1 load depends directly on copy_by_id; U load depends on copy_init_state_single→copy_init_state→copy→copy_by_id. Thus no literal independent 50/50 claim. Common GLUE is an unresolved factor, not an excluded half.

**R5-01** `bcc1a2af3fe13599b88acabc78c33e1394407dc5` = exact U Hbuf + exact R1 Hcopy/GLUE; store/load and main constructor/reset exactly U. This differs substantially from R4 A (which kept an ID buffer and added private assigns registration). No R4 A extension is copied.

**R5-02** `899ffb5f26b79e89cec1b7cc537d54be494ab390` = exact R1 Hbuf + U Hcopy policy adapted only at the existing by-ID boundary + exact R1 GLUE. `copy_by_id` core equals U `copy` core after the single required `bless(to_ptr,1)` → `bless_by_id(to_obj,to_offset,1)` substitution. Bless predicate/body after argument capture is unchanged U/R1. This is an adapted half rollback, not byte-identical U helpers.

## Reconstruction (in-memory bytes, no third candidate or CI)

STATIC-AUDIT.py selects whole Hbuf regions and whole copy/bless region, verifies both composition orders and unchanged remainder. R1/R1 gives exact R1 SHA256 `d565a600e34ef6199f4c6e0a799a5eb9a224ec0ed9a563ef47da2cbbe908cc06`. U/U **after removing unnecessary GLUE** gives exact U and V02 runtime SHA256 `88f260ddc5b315a32e64b0f6f396451373d2fb54f1a4898233508ebd81cd993c`. The entire V02 tree is not U: R1 compiler emission remains in V02. U/U-with-GLUE (U buffer + R5-02 policy+GLUE) hashes `a240b5a262e7959f0fce1dfaa1a4eb546c375d2fa7abd13a579432a9a95280be`; replacing the wrappers/by-ID split by exact U copy/bless yields U byte-for-byte. This proves textual coverage/reconstruction only, not actual retained paths, equivalence or compilation. U/U-with-GLUE is not committed/published/requested for CI in this stage.
