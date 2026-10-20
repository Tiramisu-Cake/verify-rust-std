# R7 S3 proof-audit canonicalization rationale

## Problem

The evidence packager currently rejects any `proof-audit.json` member larger
than 8 MiB before parsing it. Runner and driver sources can emit an indented
JSON audit with repeated observations, so JSON whitespace may cause the raw
file to exceed that limit even when the same parsed value has a compact
representation below the limit. The available S2 result does not establish
that this caused its package-upload failure.

## Bounded change

For an otherwise valid object whose `accepted` field is a boolean, only an
oversized proof-audit JSON member is eligible for canonicalization. Serialize
its parsed value as deterministic compact JSON. Proceed only when that form is
at most 8 MiB and smaller than the input. Keep the original bytes in the
archive as a collision-checked `.original-bytes` companion, and place the
canonical JSON at the original audit path. Record source and canonical paths,
SHA-256 digests, byte sizes, and the UTF-8 JSON encoding in an explicit
manifest descriptor. Inventory and input hashes cover both archived members.
The source evidence tree is read-only to this operation.

The verifier may validate this optional descriptor while retaining
compatibility with packages that lack it. Proof acceptance and completeness
rules remain unchanged. The audit retains its decoded JSON value and schema;
no observation is externalized or replaced with a reference. Invalid JSON,
invalid audit shape, a compact form still over the limit, no actual size
reduction, or a companion path collision fails with sizes and the limit stated.

## Evidence and limits

This is a source-supported packaging candidate. It is not evidence that the
change fixes the S2 failure. Establishing that requires the primary failure
diagnosis or a later actual-package test. Local synthetic fixtures establish
only canonicalization, byte preservation, inventory coverage, and verifier
integrity behavior. They do not establish proof validity or Cloud Build
behavior.

Original-byte preservation is bounded at 64 MiB, matching the verifier's explicit companion admission bound and Evidence's maximum targeted file size. Larger originals fail explicitly before canonicalization; they are not truncated. This extends the prior 8 MiB audit admission without increasing canonical metadata limits.
