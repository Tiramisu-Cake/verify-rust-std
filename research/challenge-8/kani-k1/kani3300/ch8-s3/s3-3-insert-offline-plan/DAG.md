# Full-obligation insertion DAG — none of these new obligations is proved here

All nodes bind source1b4a904, actual u8/KeyLess body and unchanged contracts.
Full b1..16/p1..16 grid, all logical byte values, frame and init goals remain.

| Node | Required checked obligation | Dependencies / status |
|---|---|---|
|D0 domain|Live initialized writable span, same-allocation provenance/alignment/nonwrap, sorted prefix, exact T/F|Caller/domain entailment OPEN|
|D1 early|Actual x>=last return, identity gives existing order/count/full frame|D0; no completed insert result|
|D2 logical gap|Actual tail.read/tmp/guard fields establish held x and value-accounting gap|D0; not an actual-init-bit assertion|
|D3 step|Actual copy/guard update preserves relation, footprint and bounds; moved values>x|D2; no assumed invariant/ghost store tracker|
|D4 stop|Actual decreasing sift stops at g0 or predecessor<=x|D3; bounded normal return only|
|D5 restore|Actual CopyOnDrop len1 writes held tmp into the actual gap with valid permissions|D4; no reusable qualified Drop summary supplied|
|D6 full post|Checked exact sequence gives order and full multiplicity for every q:u8; recovers unchanged post/frame/canary|D1 orD5; lemmas unproved|
|D7 union|Checked exhaustive branch/base/length coverage within exact source/cfg/provider scope|D6; only predicate arithmetic checked here|
|D8 callers|Exact bounded provider/wrapper or actual caller proof, initialization/frame/ownership and growth induction|D7; full N16/32/type/allocation/locality OPEN|

The root design question is the supported actual-body/loop/drop binding under
stock0aac. Logical equations and a ghost witness cannot replace it or justify
weakening PFC ensures/count/frame. A logical gap is not a physical uninitialized
byte; no typed hole reads, manual ShadowMem or flagON implementation.

Prior b487 cases are bounded SOURCE_REPORTED swap/sort4/separate-merge and fixed
negative fixtures, not universal summaries. Review0285317 approves the reporting; root admissionff193cc now qualifies one
exact allinit functional/known-value-frame case at bounded SOURCE_REPORTED scope.
It establishes no independent init or provider summary. Partial merge diagnostics remain INIT_OPEN/nonproviders. None supplies
insert/Drop/caller or all34 sort8 initialization contexts. Methodplan d8f4's
enabled-init storage/layout/negative-mask prerequisites remain separate and OPEN.
