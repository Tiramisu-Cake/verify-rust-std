# Native C1 binding initial run — preproof admission refusal

Build7456e9be-368f-46b5-80df-afd9d7fb84ef, proof=infra
e7290456d53e47f9e22e25e52247d1823a14a540. Create22:34:54.978676114Z;
finish22:41:21.477697Z; charged387Cloudseconds; cumulative749/3600.
Canonical archive integrity verified, SHA
b3b903c97877e92c5fd62503716b04ed1eb15abcbd3303937baed34d669a9796.
Bound translator3efc917dd38518c7cc94d12b71bb18bd26ab64e32323799e504e7f0a7e4d0ba8;
patch ed95e901c89daabffa725e1c1f38369930693b72be1d60d3548811ebafabb7ec;
kernel37ed unchanged. Fresh console/effective profile recorded in raw artifact.

Exact normal/readonly MIR fingerprints and paired refinement/source gates pass.
Default-off preserves strict entry172 unresolved outer type. Mandatory source
mutation, extra body, malformed opt-in and mixed old/new profile all refuse at
expected admission, before target; these are not semantic negatives.
Positive and both after-call controls stop at original AST SHA admission before
binding/proof: actualfc2d58d080d63cb0e95f65c626a2567f0cb156a91b60b22a9fd1d2231f8de24b,
74430bytes; expected18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5,
74422bytes. Both control artifacts exactly equal positive, deterministic.

Independent full-byte diff has only two changes: early generic preprocessing
inserts strict scope marker at cmp entry172 and consumes source212 cut into
Goto47/shortened block plus external Label47/Noop. Contract, declarations,
actual call and ghost recovery otherwise identical. Capture mode intentionally
retains the exact source cut until its own projection; native-bound had not
been routed through this same source-specific cut admission. Blind fingerprint
replacement would also leave incorrect matcher/control flow and is rejected.

Reviewed narrow correction: ONLY this exact bound mode joins capture's
exact-one cmp/source212 cut-retention branch. Existing bound rewrite then
constructs checked strict child once, preserving all normal/goto/unwind escape,
free and cleanup checks. Keep original18973 preAST gate. Default-off generic
strict processing remains unchanged. This is a source-specific placement fix;
no general inference/kernel/MU/alias/strict rule change. Next fresh run must
confirm18973 and independently inspect projected postAST before proof credit.
Native C1 normal/unwind/current/nativeposts/unit/free/leak NOT_RUN; C4 NOT_RUN.
