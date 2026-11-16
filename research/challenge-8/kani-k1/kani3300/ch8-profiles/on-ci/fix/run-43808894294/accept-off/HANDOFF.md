# worker11 — OFF lane, одна стадия завершена

63 ACCEPTED / 0 BLOCKED_TOOL / 0 REJECTED / 0 PENDING (54 positive, 9 negative).
Run43808894294, artifact14204858070, stock Kani0aac16ef62; source166a406e22.
Исторических admissions перенесено0; independent proof credit NONE, B2 не установлен.

[ACCEPTANCE.md](ACCEPTANCE.md): построчное сравнение всех63 строк с OFF43784551069/accept-v4.
[ACCEPT.json](ACCEPT.json): полные fresh bindings, роли всех1770 unreachable,
190 SAT covers и209 successful unsupported; source/tool/config identities и исходные runner/exits сохранены.

Новая merge4 leaf и consumer связаны fresh LtU8/merge4_profile instance той же OFF ветки,
текущего run и group-00 export. Предыдущий general merge leaf не заменяет новый.
Fresh qualification: regions_are_disjoint line111→114 с идентичным телом;
rejects_always_true covers по exact literal/location229/220/211, без смены oracle.
Frame failure — captured comparisons assigns.1 на helper_contracts.rs:290;
trace pointer→var_9 независимо не установлен.

[VALIDATION.json](VALIDATION.json): 17 targeted Python tests PASS; offline replay63/63.
[REVIEW.json](REVIEW.json): независимое Luna HIGH GO, read-only code/receipt review,
без reviewer replay. Source-reported policy admission не даёт independent proof credit.

Replay (Python/rg/c++filt/git only):
`python research/challenge-8/kani-k1/kani3300/ch8-profiles/on-ci/fix/run-43808894294/accept-off/intake.py`
из g0 worktree; исходные artifacts должны оставаться по пути artifact_directory в ACCEPT.json,
а pinned control доступен в /root/kani-ch8-prof02-w11.

Push/CI/публикации/ledger/local cargo-rustc-Kani-CBMC: 0.
Изменения только accept-off; файлы worker15 не затронуты.
Дальнейшие стадии в этом задании не запускались.
