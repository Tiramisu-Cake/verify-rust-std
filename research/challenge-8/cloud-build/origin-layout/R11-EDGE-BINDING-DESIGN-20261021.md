# R11 selected-call edge binding

`_mutation_plan` identifies one native ghost-command terminator by the source
invariant span and its unit destination local. `_edge_signature` instead
currently counts every ghost-command terminator in the full `insert_tail`
Body and requires exactly one. The actual source contains many annotations, so
unselected ghost calls can make setup fail before any selected-edge check.

Bind edge checks to the same selected destination local used by the plan. The
edge signature must find exactly one ghost-call terminator whose destination
is that local, then preserve only that call's `target` and `unwindAction` across
each mutation. Other ghost-command calls remain outside this check. Missing or
ambiguous selected calls stay fail-closed. This narrows the selected-call
binding without changing the source, exporter receipt, native CFG, or any
resource/placement criterion.

The same source-line ambiguity exists in `_locate_nodes`: a selected successor
block can contain the target `StorageDead` span and a different later
ghost-command terminator. Node lookup must bind the terminator's own source span
and destination to the plan's selected temporary; statement spans remain
separate evidence for `StorageLive` and `StorageDead`.

Independent GPT-6 Luna HIGH reviewer r10_review GO: own terminator source line and destination bind selected call; missing/duplicate refuse; selected target/unwind preserved, unrelated call/edges remain intact. Synthetic placement12 and overlay3 PASS. No translator semantic change or proof credit.

## BasicBlock ID field scope

The current `_block_index` calls the generic `_field_text(block, "id")`. That
helper counts textual matches across the whole nested record, so an `id` inside
the terminator's nested `FnDef` makes a valid BasicBlock appear ambiguous. Read
the balanced outer BasicBlock record, split only its top-level fields, require
exactly one top-level `id`, then parse that field's unique `index`. Nested IDs
must not count; absent or duplicated top-level IDs remain setup refusals.

Final BasicBlock own-id parser review: independent LunaHIGH GO; nested FnDef.id ignored, missing/duplicate own IDs refuse, balanced outer record and unique index retained. Current placement service13PASS, overlay3PASS.
