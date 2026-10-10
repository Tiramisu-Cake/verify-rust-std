# First composition capture — preparation failure

Build `fc01881e-62ab-49f9-913d-9036d598f872`, token
`dispatch-04c95ed5879e4e62973be6c8898a45d6`; proof=infra
`24c1c33fea23824f0f31ddcedb4f02e07a2d0625`. Create00:47:12.948071803,
finish00:52:49.843183 UTC; **337 seconds charged**. FAILURE final transport
verdict; complete archive/text inventory verified, archive
`77243263966fc2eb32a9fd9bc57f1da317c9cfb301f75e03c50d0af3851d55fa`.

Both normal/readonly export and refinement exit1 at compiler E0255: generated
`Freeze` lang-item declaration duplicates imported `std::marker::Freeze` at
verified10/import6; original10 fails likewise. No MIR/decode/AST/verifier/proof
execution after compiler failure; **new composition proof NOT_RUN**. Existing
native/C1 results unchanged. Full raw stderr retained under
`/tmp/native-compose-fc01881e-read/allprooflogs/cases/sort4-native-compose-c1/`.

Repair removes emitted duplicate only, retains pinned core Freeze definition
read/check, std import and actual FreezeMarker source, as historical native
fixture does. Additional native operation byte-certificate checks only source
mapping and do not establish caller CFG. New source requires fresh Build.
Production O26+slice tool unchanged; basef76012fb518703b1d98e243ac4f487f16877cfcb,
translator4d3a190fcec695415b41162ddf8d71aec6e2826d2b69e7692df306a568add98c,
VFcb7d9ff0a1ba281310ea4cf5694a58b99f1ebad8136b16d3007c9402ece44817;
profile baseline capture experimental/unaccepted, no new semantic overlay.
No local compiler/extraction/proof execution or repeated unchanged refusal.
