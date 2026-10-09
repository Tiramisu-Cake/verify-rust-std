# Coordinator v2 — Cloud regression result

PR2 source55414a5c8168061ad960d1f36983334e13699a12 transferred asc81fd1a5.
Tested infra/proof **e918eb875119d912b981da2bfec4e0406e06571e**;
Build **a0f40e03-fb76-4974-893b-3aad48331f7f**, SUCCESS100 conservative seconds,
create11:22:31.424859UTC /finish11:24:11.156084UTC.
Configa937693da9134270012d297b1d3b9987b5b0fb90565265e39b729ca6d6a95150;
sourceinputfed3265717c72750212917aaca055ee5ea42b4b6dbab4d80ae9ecadc18801600;
archive8e838ed8daaef679bef763435213410b1e51068986feefc527b99d59e2ae171f.

All18case outputs and full coordination log inspected; exactclient hashes match local
published inputs. SyntheticAPI/disposableCloud state only, no realparallel paidBuilds
or actualstd theorem. verification_accepted=false; dispatcherdiagnostic complete.

| Case | Result | Observed boundary |
| --- | --- | --- |
| foreign_missing_token | PASS | Foreign ledger lacks reserved token; global reservation retained |
| foreign_missing_ledger | PASS | active_token=dispatch-foreign-missing-ledger, foreign_ledger_present=False |
| foreign_uncertain_zero_matches | PASS | active_token=dispatch-foreign-uncertain-zero-matches |
| foreign_conflicting_ids | PASS | Ledger and global Build IDs conflict |
| foreign_wrong_tag | PASS | Build does not carry the reserved dispatch token |
| foreign_api_error | PASS | synthetic Cloud API unavailable |
| foreign_terminal | PASS |  |
| own_terminal_exact_charge | PASS | first_used_seconds=13, item_status=SUCCESS, second_used_seconds=13 |
| validation_rejection_owner_resume | PASS | resumed_status=NOT_CREATED_INVALID_ARGUMENT, resumed_used_seconds=0 |
| three_process_two_reservations | PASS | active_tokens=['dispatch-contender-0', 'dispatch-contender-1'], contenders=[{'result': 'reserved', 'token': 'dispatch-contender-0'}, {'result': 'reserved', 'token': 'dispatch-contender-1'}, {'result': 'blocked', 'token': 'dispatch-contender-2'}] |
| parallel_owners | PASS | owners=['foreign', 'second'] |
| one_slot_per_owner_and_ledger | PASS | same_ledger_blocked=True, same_owner_blocked=True |
| api_and_unresolved_capacity | PASS | api_token_deduplicated=True, external_builds_counted=True, unresolved_slot_counted=True |
| token_scoped_mutations | PASS | peer_preserved=True, stale_mutations_refused=True |
| legacy_state_upgrade | PASS | empty_v2_blocks_v1=True, legacy_token_preserved=True, unknown_version_refused=True |
| terminal_preserves_peer_slot | PASS | remaining_owner=second |
| cancel_owner_only | PASS | slots_retained_until_terminal=True |
| submit_capacity_gate | PASS | real_submit_calls=0, second_slot_admitted=True, third_slot_blocked_before_config=True |

Exactcontrol.pySHA f6bc8fd95a749155f2296b985db1bb242dd305e099497091bddf945078591398
coordination.pySHA 4d3f2af4490fdac6d25d6d5077bf5a7b54aeab82c090af6c81f37661cd256c07
regressionSHA 891818357a4e191ab511e6b93c832ebd0bf7ecb62b9f10b6cb38e862db56a2d1

Production firstreserve atomicallycreatedv2 underexistinglock; afterterminal
reconciliation the v2emptyenvelope is preserved. No legacyreserve existed atentry.
Legacylive migration/peerpreservation are tested synthetically, not claimed as a
liveparallelobservation. ForeignsessionSTOP and nooldclientcommands established
beforeactivation. Budgets/history/foreignstate unchanged.

## Subsequent real overlap (read-only observation)

After successful regression analysis, unrelated owner select-sort4 used compatiblev2
client and its own AFTERNOON ledger. Normal authorized merge Build1219ab51-c577-4f6f-bba5-a763d29e934a
started12:12:48.037778241Z while peer4077ed0a-75ba-4f2b-9ada-1e20a036098d
ran12:09:53.912622531Z–12:14:43.172176Z. Real execution intervals overlapped
about115seconds. Commonactive snapshot had both differentowner/ledger reservations.
Peerterminalmetadata read through Cloud API only; no peercommands/ledger/cancellation.
This observes actualtwo-build overlap, in addition to the18syntheticregression cases;
real refusal of a thirdbuild and duplicateowner were not paid experiments.
