# M2-B/S2 explicit type/signature audit

No Rust expressions, APIs, signatures, imports, integer conversions or test sources changed.
Kani delta is one Markdown handoff. Compile/build/clippy/fmt/compiler checks NOT_RUN.

The following READ-ONLY bindings were checked against supplied transformed MIR and pin source:

| Expression/API | Exact types and result |
| --- | --- |
| SpecArrayEq::spec_eq | (_1:&[u8;3], _2:&[u8;3])->bool; _3:&[u8;3]=_2; no value copy or operand swap |
| First CheckAs | _5,_6:*const[u8;3]; _7:[bool;3]; _8:fn(*const[u8;3],[bool;3])->bool; _4:bool result |
| Second CheckAs | _12,_13:*const[u8;3]; _14:[bool;3]; _15:same fn signature; _11:bool result |
| RawEq generation | uninit_visitor.rs:562–585 extracts Ref pointee Ty; byte array Ty via try_new_array unsigned U8 and checked TryInto length; unchanged code |
| body equality | _16:[u8;3]; _17:MaybeUninit<[u8;3]>; assume_init consumes _17 and returns [u8;3]; _20,&_16 and _21 are &[u8;3]; PartialEq returns bool |
| ensures comparison | closure arg _1:&closure with field0:&[u8;3]; _2:&u8; *_2: u8 compared with 7_u8, bool on both sides of &&; _6 and _5:&[u8;3]; no &closure->array conversion |
| out capture | Assert wrapper field0:&mut[u8;3], reborrow &(*_11):&[u8;3]; predicate captures shared reference, not array bytes |
| reset/live seed | existing state tracked_object_id:usize, tracked_offset:usize, value:bool; backend unsignedbv[64] on supplied model, value c_bool; live pointer_object cast to state type; pointer_offset compared to signed target zero; offset bound3 same backend unsigned type; mask array bool indexed by offset |
| RHS pointer | backend unsignedbv[8][3]* produced from canonical symbol address and offset0; AllocId key and CBMC numeric object ID not interchangeable |

No new width/sign/overflow/truncation assumption was introduced. Immutable descriptor source
Some/None/Freeze details and runtime pointer values are not supplied by these type signatures.
`OutputFormat::Old` exists in args/mod.rs:586–590. call_cbmc.rs:179–191 uses inherited
stdio for Old and skips regular JSON parser; cbmc_flags:301 forwards cbmc_args. CBMC --json-ui
and --trace are evidenced by supplied inventory/driver source. No concrete playback means no
--compact-trace injected at call_cbmc.rs:286–298. Old conflicts with export-json/SARIF/log-file;
request excludes them. This validates request construction statically, not execution or lint PASS.
