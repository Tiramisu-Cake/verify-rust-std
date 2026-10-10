# Internal VeriFast C4 selector candidate — PARTIAL

Local tool commit423d5e3cb1781ed58f8933146a555470f7b42115 on official26.10 basef76012fb518703b1d98e243ac4f487f16877cfcb. BundleSHA256e6b8e232b4e0a68af689ddde8ff2d48e0ec311e1d460ffec3df2ba08bf8493ee. Fork unavailable; this bundle replaces no existing candidate and creates no fork.

Restore in an isolated official26.10 clone with:

```sh
git bundle verify /path/to/bundle
git fetch /path/to/bundle refs/heads/research/maintainer-c4-selector-20261010:refs/heads/review/c4-selector-20261010
```

Dependency closure, three exact ordered patches, effective hashes, observed binary, Cloud commands/builds/cost, pending trust gates and session status: `research/challenge-8/cloud-build/verifast-c4-select-integration/manifest.json`. Reviews and checkpoint are next to it. Compilation and proof remain Cloud-only. This is an unaccepted partial candidate: C4 passed, current selector refused unrelated runner admission, composition not run. Corrected runner has not been executed. Previous ManuallyDrop upstream package is unchanged.
