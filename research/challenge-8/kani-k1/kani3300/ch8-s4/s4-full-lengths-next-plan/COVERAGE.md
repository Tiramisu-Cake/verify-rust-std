# Rebound exhaustive S4 coverage map

Std source `8faf8e62af8f82b5c46af020086f8df591b6757e`; admission checkpoint `8896f60ae9e0ea1c706c6b8693d00e2500190676`. Original matrix source `bd62e54df1b4749154790aa3db3cc7978f547f75`. This new view retains all100 structural rows,14 classes, all34 internal sort8 contexts and116 explicit finite typed rows; historical documents are untouched. See COVERAGE.json for exact insertion spans, absolute network bases, loop bounds and source/blob/hash citations.

Historical fallback admission `9bb6e2b7a18e338f532ec817f8acfd7515fc2fc9` covers Cell/KeyLess N0..4 on its exact old invocation. Kernel, model, partition and related spec/control bytes match the rebound source; this is dependency compatibility, not a new invocation admission. Network admission at the exact requested source covers u8/KeyLess N0..4. Both use initialized V34/base1/all34 independent full-u8; no caller/provider/generic/independent B1/B2 credit.

| Family / exact pair | Existing finite length coverage | Uncovered lengths |
| --- | --- | --- |
| Fallback Cell/KeyLess | 0,1,2,3,4 (2 historical cases) | 5,6,7,8,9,10,11,12,13,14,15,16 |
| Network u8/KeyLess | 0,1,2,3,4 (4 exact cases) | 5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32 |
| General u8/KeyLess | No S4 full-length admission in this checkpoint | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32 |
| General NonCopyByte/KeyLess | No S4 full-length admission in this checkpoint | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32 |
| General size>16 | No typed S4 admission or active whole-value model here | Shared all-size rows0..15 plus distinct sort4 rows16..32 |

An OPEN S4 row does not erase historical S1 smoke or S3 leaf results; neither substitutes for the exact S4 helper/caller/geometry. Every dispatch/geometry/provider bridge in BRIDGES.md stays open. Length matches do not transfer types, backing capacities, bases, scratch or comparators.

Notation: A=existing exact network admission; H=historical fallback admission with matching dependencies; O=open. p is relative tail offset; span=p+1. No row in the tables is a future successful result.

## Fallback: every length0..16

| N | Class | Status | Shift / insertion tails p | Next package |
| --- | --- | --- | --- | --- |
| 0 | F0 | H | none | LATER |
| 1 | F0 | H | none | LATER |
| 2 | F1 | H | offset1; 1 | LATER |
| 3 | F1 | H | offset1; 1,2 | LATER |
| 4 | F1 | H | offset1; 1,2,3 | LATER |
| 5 | F1 | O | offset1; 1,2,3,4 | F-gap1 |
| 6 | F1 | O | offset1; 1,2,3,4,5 | F-gap1 |
| 7 | F1 | O | offset1; 1,2,3,4,5,6 | F-gap1 |
| 8 | F1 | O | offset1; 1,2,3,4,5,6,7 | F-gap1 |
| 9 | F1 | O | offset1; 1,2,3,4,5,6,7,8 | F-gap2 |
| 10 | F1 | O | offset1; 1,2,3,4,5,6,7,8,9 | F-gap2 |
| 11 | F1 | O | offset1; 1,2,3,4,5,6,7,8,9,10 | F-gap2 |
| 12 | F1 | O | offset1; 1,2,3,4,5,6,7,8,9,10,11 | F-gap2 |
| 13 | F1 | O | offset1; 1,2,3,4,5,6,7,8,9,10,11,12 | F-gap3 |
| 14 | F1 | O | offset1; 1,2,3,4,5,6,7,8,9,10,11,12,13 | F-gap3 |
| 15 | F1 | O | offset1; 1,2,3,4,5,6,7,8,9,10,11,12,13,14 | F-gap3 |
| 16 | F1 | O | offset1; 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 | S4P4_CELL16 |

## Network: every length0..32

| N | Class | Status | Regions: base/L/seed/insert tails p | Merge + copy-back | Next package |
| --- | --- | --- | --- | --- | --- |
| 0 | N0 | A | return | none | LATER |
| 1 | N0 | A | return | none | LATER |
| 2 | N1 | A | b0 (V34:1)/L2/one/p1 | none | LATER |
| 3 | N1 | A | b0 (V34:1)/L3/one/p1,2 | none | LATER |
| 4 | N1 | A | b0 (V34:1)/L4/one/p1,2,3 | none | LATER |
| 5 | N1 | O | b0 (V34:1)/L5/one/p1,2,3,4 | none | N-gap1 |
| 6 | N1 | O | b0 (V34:1)/L6/one/p1,2,3,4,5 | none | N-gap1 |
| 7 | N1 | O | b0 (V34:1)/L7/one/p1,2,3,4,5,6 | none | N-gap1 |
| 8 | N1 | O | b0 (V34:1)/L8/one/p1,2,3,4,5,6,7 | none | S4P3_NETWORK_BOUNDARIES |
| 9 | N2 | O | b0 (V34:1)/L9/sort9/pnone | none | S4P3_NETWORK_BOUNDARIES |
| 10 | N2 | O | b0 (V34:1)/L10/sort9/p9 | none | N-gap2 |
| 11 | N2 | O | b0 (V34:1)/L11/sort9/p9,10 | none | N-gap2 |
| 12 | N2 | O | b0 (V34:1)/L12/sort9/p9,10,11 | none | N-gap2 |
| 13 | N3 | O | b0 (V34:1)/L13/sort13/pnone | none | S4P3_NETWORK_BOUNDARIES |
| 14 | N3 | O | b0 (V34:1)/L14/sort13/p13 | none | N-gap3 |
| 15 | N3 | O | b0 (V34:1)/L15/sort13/p13,14 | none | N-gap3 |
| 16 | N3 | O | b0 (V34:1)/L16/sort13/p13,14,15 | none | N-gap3 |
| 17 | N3 | O | b0 (V34:1)/L17/sort13/p13,14,15,16 | none | S4P3_NETWORK_BOUNDARIES |
| 18 | N4 | O | b0 (V34:1)/L9/sort9/pnone; b9 (V34:10)/L9/sort9/pnone | 18 | N-bridge1 |
| 19 | N4 | O | b0 (V34:1)/L9/sort9/pnone; b9 (V34:10)/L10/sort9/p9 | 19 | N-bridge1 |
| 20 | N4 | O | b0 (V34:1)/L10/sort9/p9; b10 (V34:11)/L10/sort9/p9 | 20 | N-gap4 |
| 21 | N4 | O | b0 (V34:1)/L10/sort9/p9; b10 (V34:11)/L11/sort9/p9,10 | 21 | N-gap4 |
| 22 | N4 | O | b0 (V34:1)/L11/sort9/p9,10; b11 (V34:12)/L11/sort9/p9,10 | 22 | N-gap4 |
| 23 | N4 | O | b0 (V34:1)/L11/sort9/p9,10; b11 (V34:12)/L12/sort9/p9,10,11 | 23 | N-gap4 |
| 24 | N4 | O | b0 (V34:1)/L12/sort9/p9,10,11; b12 (V34:13)/L12/sort9/p9,10,11 | 24 | N-bridge2 |
| 25 | N5 | O | b0 (V34:1)/L12/sort9/p9,10,11; b12 (V34:13)/L13/sort13/pnone | 25 | N-bridge1 |
| 26 | N6 | O | b0 (V34:1)/L13/sort13/pnone; b13 (V34:14)/L13/sort13/pnone | 26 | N-bridge2 |
| 27 | N6 | O | b0 (V34:1)/L13/sort13/pnone; b13 (V34:14)/L14/sort13/p13 | 27 | N-gap5 |
| 28 | N6 | O | b0 (V34:1)/L14/sort13/p13; b14 (V34:15)/L14/sort13/p13 | 28 | N-gap5 |
| 29 | N6 | O | b0 (V34:1)/L14/sort13/p13; b14 (V34:15)/L15/sort13/p13,14 | 29 | N-gap5 |
| 30 | N6 | O | b0 (V34:1)/L15/sort13/p13,14; b15 (V34:16)/L15/sort13/p13,14 | 30 | N-gap5 |
| 31 | N6 | O | b0 (V34:1)/L15/sort13/p13,14; b15 (V34:16)/L16/sort13/p13,14,15 | 31 | N-close |
| 32 | N6 | O | b0 (V34:1)/L16/sort13/p13,14,15; b16 (V34:17)/L16/sort13/p13,14,15 | 32 | N-close |

## General: every length/size case (50 rows)

Each `all`/`<=16` row needs separate concrete u8 and NonCopyByte evidence. All are O. The17 `>16` rows require another typed whole-value model and preserve sort4 rather than sort8. Scratch sizes are minimum legal views for n>=2; wrapper uses48.

| N | Size | Class | h/r | Seed / p in left; right | Final merge | Min scratch |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | all | G0 | - | return; pnone / pnone | none | 0 |
| 1 | all | G0 | - | return; pnone / pnone | none | 0 |
| 2 | all | G1 | 1/1 | copy1; pnone / pnone | 2 | 18 |
| 3 | all | G1 | 1/2 | copy1; pnone / p1 | 3 | 19 |
| 4 | all | G1 | 2/2 | copy1; p1 / p1 | 4 | 20 |
| 5 | all | G1 | 2/3 | copy1; p1 / p1,2 | 5 | 21 |
| 6 | all | G1 | 3/3 | copy1; p1,2 / p1,2 | 6 | 22 |
| 7 | all | G1 | 3/4 | copy1; p1,2 / p1,2,3 | 7 | 23 |
| 8 | all | G2 | 4/4 | sort4; pnone / pnone | 8 | 24 |
| 9 | all | G2 | 4/5 | sort4; pnone / p4 | 9 | 25 |
| 10 | all | G2 | 5/5 | sort4; p4 / p4 | 10 | 26 |
| 11 | all | G2 | 5/6 | sort4; p4 / p4,5 | 11 | 27 |
| 12 | all | G2 | 6/6 | sort4; p4,5 / p4,5 | 12 | 28 |
| 13 | all | G2 | 6/7 | sort4; p4,5 / p4,5,6 | 13 | 29 |
| 14 | all | G2 | 7/7 | sort4; p4,5,6 / p4,5,6 | 14 | 30 |
| 15 | all | G2 | 7/8 | sort4; p4,5,6 / p4,5,6,7 | 15 | 31 |
| 16 | <=16 | G3S | 8/8 | sort8; pnone / pnone | 16 | 32 |
| 16 | >16 | G3L | 8/8 | sort4; p4,5,6,7 / p4,5,6,7 | 16 | 32 |
| 17 | <=16 | G3S | 8/9 | sort8; pnone / p8 | 17 | 33 |
| 17 | >16 | G3L | 8/9 | sort4; p4,5,6,7 / p4,5,6,7,8 | 17 | 33 |
| 18 | <=16 | G3S | 9/9 | sort8; p8 / p8 | 18 | 34 |
| 18 | >16 | G3L | 9/9 | sort4; p4,5,6,7,8 / p4,5,6,7,8 | 18 | 34 |
| 19 | <=16 | G3S | 9/10 | sort8; p8 / p8,9 | 19 | 35 |
| 19 | >16 | G3L | 9/10 | sort4; p4,5,6,7,8 / p4,5,6,7,8,9 | 19 | 35 |
| 20 | <=16 | G3S | 10/10 | sort8; p8,9 / p8,9 | 20 | 36 |
| 20 | >16 | G3L | 10/10 | sort4; p4,5,6,7,8,9 / p4,5,6,7,8,9 | 20 | 36 |
| 21 | <=16 | G3S | 10/11 | sort8; p8,9 / p8,9,10 | 21 | 37 |
| 21 | >16 | G3L | 10/11 | sort4; p4,5,6,7,8,9 / p4,5,6,7,8,9,10 | 21 | 37 |
| 22 | <=16 | G3S | 11/11 | sort8; p8,9,10 / p8,9,10 | 22 | 38 |
| 22 | >16 | G3L | 11/11 | sort4; p4,5,6,7,8,9,10 / p4,5,6,7,8,9,10 | 22 | 38 |
| 23 | <=16 | G3S | 11/12 | sort8; p8,9,10 / p8,9,10,11 | 23 | 39 |
| 23 | >16 | G3L | 11/12 | sort4; p4,5,6,7,8,9,10 / p4,5,6,7,8,9,10,11 | 23 | 39 |
| 24 | <=16 | G3S | 12/12 | sort8; p8,9,10,11 / p8,9,10,11 | 24 | 40 |
| 24 | >16 | G3L | 12/12 | sort4; p4,5,6,7,8,9,10,11 / p4,5,6,7,8,9,10,11 | 24 | 40 |
| 25 | <=16 | G3S | 12/13 | sort8; p8,9,10,11 / p8,9,10,11,12 | 25 | 41 |
| 25 | >16 | G3L | 12/13 | sort4; p4,5,6,7,8,9,10,11 / p4,5,6,7,8,9,10,11,12 | 25 | 41 |
| 26 | <=16 | G3S | 13/13 | sort8; p8,9,10,11,12 / p8,9,10,11,12 | 26 | 42 |
| 26 | >16 | G3L | 13/13 | sort4; p4,5,6,7,8,9,10,11,12 / p4,5,6,7,8,9,10,11,12 | 26 | 42 |
| 27 | <=16 | G3S | 13/14 | sort8; p8,9,10,11,12 / p8,9,10,11,12,13 | 27 | 43 |
| 27 | >16 | G3L | 13/14 | sort4; p4,5,6,7,8,9,10,11,12 / p4,5,6,7,8,9,10,11,12,13 | 27 | 43 |
| 28 | <=16 | G3S | 14/14 | sort8; p8,9,10,11,12,13 / p8,9,10,11,12,13 | 28 | 44 |
| 28 | >16 | G3L | 14/14 | sort4; p4,5,6,7,8,9,10,11,12,13 / p4,5,6,7,8,9,10,11,12,13 | 28 | 44 |
| 29 | <=16 | G3S | 14/15 | sort8; p8,9,10,11,12,13 / p8,9,10,11,12,13,14 | 29 | 45 |
| 29 | >16 | G3L | 14/15 | sort4; p4,5,6,7,8,9,10,11,12,13 / p4,5,6,7,8,9,10,11,12,13,14 | 29 | 45 |
| 30 | <=16 | G3S | 15/15 | sort8; p8,9,10,11,12,13,14 / p8,9,10,11,12,13,14 | 30 | 46 |
| 30 | >16 | G3L | 15/15 | sort4; p4,5,6,7,8,9,10,11,12,13,14 / p4,5,6,7,8,9,10,11,12,13,14 | 30 | 46 |
| 31 | <=16 | G3S | 15/16 | sort8; p8,9,10,11,12,13,14 / p8,9,10,11,12,13,14,15 | 31 | 47 |
| 31 | >16 | G3L | 15/16 | sort4; p4,5,6,7,8,9,10,11,12,13,14 / p4,5,6,7,8,9,10,11,12,13,14,15 | 31 | 47 |
| 32 | <=16 | G3S | 16/16 | sort8; p8,9,10,11,12,13,14,15 / p8,9,10,11,12,13,14,15 | 32 | 48 |
| 32 | >16 | G3L | 16/16 | sort4; p4,5,6,7,8,9,10,11,12,13,14,15 / p4,5,6,7,8,9,10,11,12,13,14,15 | 32 | 48 |

## All34 same-scratch internal merge8 contexts

| General N | Left (src,dst) in S | Right (src,dst) in S |
| --- | --- | --- |
| 16 | (16,0) | (24,8) |
| 17 | (17,0) | (25,8) |
| 18 | (18,0) | (26,9) |
| 19 | (19,0) | (27,9) |
| 20 | (20,0) | (28,10) |
| 21 | (21,0) | (29,10) |
| 22 | (22,0) | (30,11) |
| 23 | (23,0) | (31,11) |
| 24 | (24,0) | (32,12) |
| 25 | (25,0) | (33,12) |
| 26 | (26,0) | (34,13) |
| 27 | (27,0) | (35,13) |
| 28 | (28,0) | (36,14) |
| 29 | (29,0) | (37,14) |
| 30 | (30,0) | (38,15) |
| 31 | (31,0) | (39,15) |
| 32 | (32,0) | (40,16) |

Each interval is length8; src is temp storage initialized by two sort4 calls. The final general merge uses S -> V, while network merge uses V -> private stack then copies back. These opposite directions and each base/capacity remain separate proof scopes.

After a hypothetical admitted S4P3 the network union would be0..4 plus8,9,13,17 (9 lengths); residuals would be5,6,7,10,11,12,14,15,16,18..32. After separately admitted Cell16, fallback residuals would be5..15. These are projections only; current map remains unchanged.
