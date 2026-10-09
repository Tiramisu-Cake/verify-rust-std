# FRAME-shadow capture setup correction

Build bb8d295e-40d1-4b6f-927d-11054739c6bf failed before source extraction: the shadow preparer directly reads O26-R3-FRAME-TEST.json but the capture selection omitted it. This is setup failure, not an intended negative. All source preparer imports, provider loads, and the collector literal profile reads were reviewed; the two new direct JSON reads and all inherited prepare/capture/owner-projection files are selected. No guards were removed. Archive 1c7aae5eb330b851a559fb3b7b789dbba78b114e1f82b93b3096495da7b3b45e and text index 27a5ae0f06802ac26a4925e0a91d5cbc39d33ce6bd0258362be55f434c9ca6e7 fully verified. Cost 318s; phase total 1437/3600s.

The repeat adds the missing parent manifest and explicitly disables the prepared FRAME-shadow proof switch in capture. It retains the same source transform and diagnostic capture contract. No proof claim or new trusted rule.
