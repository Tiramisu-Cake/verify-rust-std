# Frozen-profile source-console cache — design before implementation

## Objective and scope

Avoid repeating the roughly 100-second VeriFast console compilation for the
same frozen W1/M2/C1/cleanup hosted profile. The cache stores exactly one file:
the source-built `bin/verifast` executable whose admitted SHA-256 is
`3a08722cedc2f07daf26dfde2f46b8710662028ca5924212c4d1d92d68b70f1a`. It does
not store or restore a source tree, OCaml objects, generated files, exporter,
refiner, Z3, VFdeps, decoder, toolchain, runtime resources, or verifier results.

Each run still fetches the pinned VeriFast commit into a fresh source tree,
checks the original source files, applies and verifies every pinned patch,
records the patched source and toolchain inputs, and checks the current release
exporter/refiner and the actual runtime dependencies. A cache hit replaces only
the final console `make` invocation. The binary SHA, source and patch profile,
toolchain fingerprint, manifest schema and hosted runner identity must all
match before the helper copies it into the fresh tree. Every invalid or absent
cache is a recorded miss followed by the existing cold build. A cold output is
published only when its bytes match the admitted console SHA.

The source tree lacks `bin/libz3.so` before `make`. The build helper now mirrors
the pinned GNUmakefile's `Z3_DLL_DIR` lookup, requires the resolved directory to
be the freshly unpacked VFdeps `lib`, checks that `libz3.so` against its
observed pinned digest, and stages that same file into the fresh source tree
before profile creation. The existing post-build `ldd` path check remains in
force. This cache never supplies Z3.

## Trust and keying

The helper is hosted-Linux-only, like `build.sh`. Its input profile is a
canonical, path-free manifest made after the source patch chain and pinned
build toolchain have been checked. It records the profile ID, Ubuntu version,
VeriFast commit, hashes of all four patch files, original and patched audited
source/spec files, the applied patch, release console/exporter/refiner pins,
VFdeps archive, decoder revision and toolchain fingerprint. The cache sidecar
must carry this profile digest, the exact admitted console digest, and a
well-formed producer `GITHUB_SHA`. A cache directory has exactly `verifast`
and `manifest.json`, both regular non-symlink files. The consumer verifies all
metadata and the payload hash before copying; it then rechecks the installed
bytes. The producer Actions SHA is provenance, not permission to override the
current input profile.

The workflow integration should use a profile-versioned cache key and supply
its restored directory as `VF_CONSOLE_CACHE_DIR`. A stale key cannot bypass the
helper's current-profile comparison; it causes a cold build. The restore step
never alters a cache directory on a miss. After a cold success, publication
may fill an absent or empty directory for Actions to save; a nonempty or
non-directory destination remains untouched. The helper never trusts a cache
hit to supply source or runtime resources. An output with any other hash
remains usable only through the existing cold-build path and is not cacheable.

## Fail-closed evidence matrix

The hosted helper self-check accepts a manifest only for the exact expected
profile and producer-SHA syntax. It rejects a wrong profile digest, wrong
console digest, malformed producer SHA, extra file, symlink, missing payload,
or one-byte payload corruption. Restore reports each invalid case as a miss
without installing any bytes. Publication refuses an existing cache entry and
refuses an output with the wrong admitted SHA. Cache-hit and cold-build paths
both retain the existing source, patch, toolchain, output hash, `ldd`, Z3 path,
and helper-binary evidence; the build-mode evidence distinguishes a skipped
compile from a successful `make`.

No script is run on the editing server. Initial rollout should collect one
hosted cold producer record and one cache-hit record before relying on the
saved time; if the current workflow cannot supply immutable producer artifacts
or the expected profile directory, keep the cache disabled and use the cold
build.
