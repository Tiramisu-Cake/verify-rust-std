# Candidate6 — exact caller boundary delta

Independent GPT-6 Luna HIGH, fork_turns=none, no children: GO.
The six checked recovery commands are unchanged from candidate5 review.
Anchor now includes the unique following old.WRAPPER_SIGNATURE, binding the
insert_tail closing braces immediately before the actual caller. Replacement
preserves the wrapper signature; earlier identical helper braces are excluded.
Archived Build4 source310-321, SHA dad3145c1164ac7a5f901ce6966200b4fbff6c39081f70bdae280d14903acea6,
file2d78ebdaeb062e188723dd979753b6ca3c2142a8d584603f17f4536298dbcdd1,
request141b6b69453eca3d5f1be94c80768ac4870b8cabc81ffd606b981c688b1b356b
confirms loop/branch/function close316/317/318, blank319, exactwrapper320.
These coordinates do not establish parser-input binding or proof acceptance.
Synthetic2 tests preserve unrelated helper braces and reject missing/ambiguous
wrapper boundaries; static18patch/18base/source-pin composition PASS. No actual
local preparation/compiler/proof. Tool/profile unchanged; qualificationOPEN.

first-callback.py SHA: 4741c91882ffaae02138b34f6ac639ab2df0679969bf50dfbecdcfcf9ea3e0f1
