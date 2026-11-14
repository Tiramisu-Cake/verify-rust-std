# S5 static review / stop disposition

Source/contract/flag/matcher review performed; two bounded Luna High read-only investigations
covered strong cases and modes. No independent semantic-candidate review was run because no
source candidate exists. Their findings confirm missing exact-base Replace outcome and unresolved
strong-hole total counts; old manifests cannot justify a 2/3 alternative in expected.

Matcher audit: tools/compiletest/src/runtest.rs::verify_output/contains_lines/contains uses literal
substring matching; `\` chains consecutive lines, patterns elsewhere may occur in any order.
Repeated patterns do not count duplicates and no extra-output exclusion exists. Required golden
form is ID/function-prefix + Status + Description blocks, anchored SUMMARY/`** N of`, verdict and
single-harness completion. No regex, full stdout snapshots, std line/toolchain/host pins or blessing.

Frame portability needs reviewed role binding for outside assign vs next allowed out assign;
old var_7/var_8 alone should not substitute for target identity. Positive mode covers must select
SATISFIED generated copies. Negative copies may remove pure observation hooks only.

Mixed disposition is explicit: eventual removal reduces exported end-to-end inventory coverage;
per-root semantic replacement does not prove mixed isolation. Coordinator must assess the stated
tradeoff in MIXED-ISOLATION-DISPOSITION.md before acceptance. No controls have been removed now.

Result: STOP BEFORE DELETION, not READY. No source commit or weakening made.
