# S1-05 — offline acceptance review, run 43864841077

**Qualified acceptance remains PENDING; proof credit is NONE.** The offline replay found 35 requested rows in 14 groups. Four groups have complete rich inventories and exact property coordinates; the other ten groups have incomplete decoder records with missing file/line data. The nine rows in the four complete groups remain pending. Six have source-reported SUCCESS verdicts; three match their sole predeclared negative oracle exactly.

Inputs are pinned to control `8860d38558651f7cf2e292d57b06b378c6ad3b94`, std `5be85699b8826e3286c0bf89efb9affefac0acb5`, and Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`. Request SHA256 is recorded in [ACCEPT.json](ACCEPT.json). The replay checks request/source/control identities, changed-file and payload hashes, same-run source snapshots, receipt/export/rich evidence hashes where present, complete property inventories, and exact oracle/property coordinates. It reads only saved structured JSON; no stdout/stderr logs or previews are read. Kani, CBMC, cargo, and rustc were not run.

## Evidence available from complete groups

- All **41 required cover messages** map to one exact same-run `SATISFIED` property ID, description, source file, and line. This establishes reachability for those covers; it does not establish domain completeness.
- **4 of 35 required-success messages** map by exact source assertion call site to a unique same-run successful placeholder property: three `corruption_companion` assertions and `S1_COUNT_FIXTURE_STAYS_SORTED`. The other 31 literals are retained at pinned source sites but do not map to an individual property without ambiguity. Macro-generated properties share the invocation coordinate, and some direct source lines generate multiple properties. No count or ordinal binding is used.
- The three expected negative outcomes are exact sole-failure matches against their predeclared IDs, classes, descriptions/sites, and source/variant evidence: `order_corruption_rejected`, `count_corruption_rejected`, and `activation-default`. Their observation is recorded as `EXPECTED_EXACT_PREDECLARED_ORACLE`, not as qualified acceptance. The corruption negatives have their same-run source-success companion; the activation companion has only an incomplete rich inventory in `light-controls-u34`.
- Successful unsupported-construct properties are linked by exact ID, class, status, file, and line within the same harness. The allowed SUCCESS records do not themselves block acceptance.

## Remaining gates

The complete groups retain 46 unreachable records: 20 exact sites in `active_post`, 25 other check sites whose role remains UNKNOWN, and one unreachable mutant return cover. The 20 `active_post` sites occur in the three expected-negative scenarios. Their exact source identity is established, but whether each is mandatory for that negative scenario remains **PENDING**; the review does not call them confirmed blockers based on the function name alone. The other 25 sites are not exempted because their IDs look like helpers. Their role and scenario relevance remain UNKNOWN. The return cover under the false-contract mutant is expected to be unreachable after the mutation; it supplies no positive coverage credit.

The three PFC rows in these groups (`stable_default_cell`, `unstable_default_cell`, and `activation-default`) still need exact check/modifies wrapper and target/contract-chain binding. The activation mutation also lacks a complete rich companion inventory. The six successful positive observations still need remaining success-message bindings and unreachable-role review. There are **0 confirmed mandatory-blocker rows** and **0 qualified rows**; the applicable gates remain pending or unknown as recorded per row.

For the ten incomplete groups, acceptance is withheld because rich property records lack decoder file/line fields and are marked INCOMPLETE. This includes `light-controls-u34` (9 rows), eight two-row freeze groups (16 rows), and `activation-override-u34` (1 row). Their source-level verdicts do not substitute for complete named inventories.

The full row-by-row record includes exact unreachable IDs/sites and their role/applicability findings, all required-message bindings, companions, negative oracles, source verdicts, and concrete pending reasons in [ACCEPT.json](ACCEPT.json). Replay it with:

```sh
python3 accept/intake.py
```

No historical receipts or ledgers were modified, and no independent B1/B2 proof credit is claimed.
