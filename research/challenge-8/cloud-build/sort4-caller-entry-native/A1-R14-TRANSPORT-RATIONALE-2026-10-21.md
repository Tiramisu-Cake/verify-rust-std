# R14 lossless source encoder tuning

Static unpublished Git snapshot6a97ed5603b571461bbe05e1954ac3ab0ba40734 preserved all selected paths/objects but produced574482bytes, exceeding unchanged191×3990 base64 source transport capacity (maximum571567bytes). No dispatch occurred. Runtime closure contains no unused historical Markdown prose; no input is removed.

Keep utf8-xz-envelope-v1, all object schemas, byte/OID/size/closure validation, decoder128MiB memory bound,64MiB decoded bound, caps and dependencies. Tune only standard LZMA2 encoder options: existing preset6 with EXTREME and pb=0, keeping its8MiB dictionary. Same decoder accepts the standard XZ stream and yields identical bytes. Measured on identical3579335byte inner payload: preset6=574482bytes, preset6EXTREME=571772, preset6EXTREME/pb0/lc3=570293. This is a source-preserving encoder setting, not a new codec or a cap increase. Final committed candidate still requires complete static restore and exact byte equality for every selected path plus full dispatch-token/config checks.

No proof or tool semantics change; no formal credit. Existing corrupt/ambiguous/truncated/size/OID decoder controls remain mandatory. Whole compressed evidence cap536870912 is separate from this source input transport.
