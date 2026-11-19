# Internal status draft — not for publication

Experimental SmallSort work has admitted four exact bounded source-reported
network cases (N0..1, N2, N3, N4), using initialized V34/base1, full-domain u8
values and KeyLess. They check sortedness, full-value multiplicity and the
outside frame/canary. In run44548842328, the concrete-call version completed
these cases in3–33s native verification; the earlier version hit600s whole-child
timeouts. Those censored results do not support an exact speedup factor.

This evidence uses experimental std `8faf8e62af` and stock Kani `0aac16ef62`.
**#752 remains at `872d5a4338`; these results cannot be attributed to the current
PR without integration and compatible qualification.** The run's workflow
FAILURE/SELECTED_PARTIAL/strict0of8 remains unchanged by separate admission.

The criteria map records admitted trait smoke, helper and caller cases alongside
the missing full fallback/network/general domains and contract composition.
Bounded leaves are not automatically summary providers. General/threshold-wide
proof, initialization, invalid values, immutable writes, ownership/panic/Drop
and independent B1/B2 credit remain open at the broader scope. Next is a
separately authorized integration/proof plan within existing caps; no PR edit,
publication or new run is authorized by this draft.
