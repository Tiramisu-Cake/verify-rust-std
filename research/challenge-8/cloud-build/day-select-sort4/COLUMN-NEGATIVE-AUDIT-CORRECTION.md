# Evidence-stage audit correction — NOT_RUN

Observed b23 wrong-first full log: exact ordered-route Fatal, exit2, immutable
source/unit admission and scope marker, no proof header and no receiver marker.
Actual source ghost calls155 precede as_mut_ptr173/174; the fault stops translator
before receiver admission. The previous audit incorrectly required that later
marker. Correct only this temporal expectation: require exact Fatal, exit2, scope,
no receiver/header, route marker count0 for wrong-first/missingcandidate,1 for
wrong-second. No source/tool semantic or target contract change; no checks deleted.
The raw b23 wrong-first observation supports only that case. Wrong-second and
missingcandidate controls plus nested scheduling remain unexecuted; complete
combined gate is NOT_RUN. No additional hosted check in this closing session.
