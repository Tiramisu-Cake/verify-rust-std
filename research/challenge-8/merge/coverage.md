# Independent merge geometry coverage

Before first hosted acceptance, every mathematical proof below is a draft.

| Obligation | Planned or established evidence | Boundary |
| --- | --- | --- |
| Exact active Rust schedule | Full-source SHA32574f..., active operation certificate for three functions | Hosted admission pending; no Rust AST/MIR/refinement proof |
| merge_up access/advance | Both reference reads, selected copy source/write BEFORE right/left/dst add; arbitrary normal Boolean | Pure integer positions only |
| merge_down access/advance | Both reads/copy/write BEFORE right/left wrapping_sub and ordinary dst.sub | Requires dst>=1 for ordinary sub; actual caller proves this |
| Arbitrary-length paired loop | Count invariant and structural induction over arbitrary decision list of length n/2 | No bounded enumeration/SWO; draft until hosted certificate |
| Odd residual/endpoints | Both sources readable, dst=n/2, selection/advancement and terminal boundary guards | Arbitrary residual Boolean handles ZST comparison uncertainty geometrically |
| Destination geometry | Forward/reverse disjoint intervals, odd gap, exactly n writes | No physical write/initialization/resource theorem |
| Scalar final checks | Even a=d; odd a+h=d, exact scalar h=a<d supplemental | Not automatically pointer equality/order, particularly ZST |
| Negative controls | Read at n, invalid advance, exact proof predicate/location controls | Concrete witnesses calibrate classifier, not universal proof |
| Actual Rust memory/unwind/functionality | None | Provenance/overflow/ZST/permissions/initialized T/ownership/FnMut/panic and sorting OPEN |

Networks proof/budget ledger is frozen separately; no transfer of its remaining
seconds or status to this phase. Current own [STATUS](STATUS.md), [plan](PLAN.md),
[source map](SOURCE-MAP.md), [integration obligations](INTEGRATION.md).
