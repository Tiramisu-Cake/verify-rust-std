# Slice 06 compile seams

Candidate `3f5242bb1539fb88196d7e503b722f0905f2b46c`, parent
`96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f`. No native tool was invoked.

Production delta is empty. Compiler/library files, dependencies, workflows, and all
inherited test inputs/goldens are parent-identical. The existing48 call contracts
are inherited verbatim from accepted5; no interface or expected count changes.
Both reusable checker runs PASS: parent→head6 inventories11 Rust fixtures;
B1→head6 inventories190 changed Rust files and the cumulative declaration/import/
impl seams. Both also check all explicitly bound compiler consumers. Ten synthetic
Python checker tests PASS. Reports bind source, checker and contract hashes.

All imports, declarations and impl headers in the eleven new fixtures are exact F.
Union constants and variables use custom MIR calls to the same `consume(Byte)`
body; legal inputs read byte0, hole inputs read the empty-field union as a byte.
The constant-assignment branch at visitor F420–424 belongs4 and is already present;
the complete visitor blob equals F and accepted5. No duplicate branch is added.

Raw-field tests form raw addresses, preserve `Pair`'s actual offsets4/8 and size12,
write/read only `value`, then distinguish the untouched tail and padding. The
existing owner4 `address_of_raw_deref`/`visit_ordinary_assignment` guards and setters
remain unchanged. They neither create an initialized parent reference nor mark
the whole aggregate initialized.

Borrowed DST cases call `read(&mut [MaybeUninit<u8>])`: initialized payload succeeds,
hole payload reaches the uninitialized-read boundary. By-value cases retain the
`unsized_fn_params` trait/impl signatures from F and pass `*source`, not its box or
fat pointer. Both initialized and hole inputs require the explicit unsupported-size
diagnostic. Owner4's argument-size/transfer guards and unit remain unchanged.

The three pre-F7 import/writer snippets remain exact `PRE-F7.json`. No journal,
scope API, RAII wrapper or `replace_delayed_body` is introduced. Residual verification
compares every complete five-file zero-context patch to the pinned historical F7
patch bytes, including all14 hunk headers, rather than permitting arbitrary changes
to those filenames. Alternate-index application yields the exact F tree without
altering the source worktree or creating a stage7 commit.

These are bounded source-token/identity checks plus manual review. They do not
expand custom MIR/macros, resolve Rust symbols, check types/traits/borrows, bind MIR
or establish compilation. Native fmt/build/clippy/units/Quick are NOT_RUN on head6.
