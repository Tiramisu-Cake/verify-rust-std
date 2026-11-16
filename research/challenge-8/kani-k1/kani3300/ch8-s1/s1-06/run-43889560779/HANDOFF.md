# Handoff — S1-06 intake

Стадия intake и офлайн-классификации run `43889560779` выполнена. Вход g0
`f58f131cfa575698617e551707f665445a454625`. Все новые файлы находятся в этой папке;
исторические evidence/receipts/ledgers не изменены.

Executed control `a14a513eb7a77297a0cc10ff6eefa7577c2c383c` — sibling исходного fix
`b25dd39a46ba90b167500997d546a5f2f5bd8f3b` с идентичным tree. Сохранены request,
run/job/artifact metadata, 14 original compact artifacts, exact export/properties
projections и receipt projections без stdout/stderr previews. ZIP digests сверены
с GitHub по загруженным ZIP bytes до извлечения; сами ZIP не сохранялись. При
replay проверяется записанная download attestation и payload/member hashes,
а не повторно вычисляется отсутствующий ZIP digest.

Повторить структурную сверку из любой cwd:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/s1-06/run-43889560779/intake.py
PYTHONDONTWRITEBYTECODE=1 python3 /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/s1-06/run-43889560779/accept/intake.py
```

Требуются неизменённые local pins `/root/kani-ch8-s1-06-intake-w13` (control a14)
и `/root/verify-rust-std-ch8-s1-04-w13` (std 5be). Это только structured JSON/static
replay, verifier не запускается. `runner-collected.json` сохраняет исходный
fail-closed результат коллектора; `collected.json` отдельно добавляет source
verdict каждой строки, retained inventory, исходные exits и измерения.

9986/9986 properties сохранены; verdicts 27 SUCCESS / 8 FAILURE. Все 16 heavy
строк source SUCCESS, child exits0. Непосредственный runner failure во всех
8 heavy-группах — metadata completeness; точная причина есть в receipt и
collected.json. Rich.error=null не означает completeness PASS.

18 nullable sites (16 heavy + production/mutated stable_freeze_activation) —
stock MIR unreachable guards, status SUCCESS. Они не являются required
post/frame/relation/covers; подробности и обе exact IDs — missing-sites.json,
STOCK-ROLE.json. Site `lib.rs:0:0` не восстановлен по имени/соседней строке.
Текущий completeness gate не ослаблен. Варианты политики для координатора
сформулированы в POLICY-QUESTION.md и **не применены**.

Офлайн-классификация w11 — accept/ACCEPT.json и accept/ACCEPTANCE.md. Qualified
acceptance PENDING, proof credit NONE. Source SUCCESS и exact negative-oracle
observations не заменяют остальные gates. 10 failed-групп не имеют after-run
binary snapshots; даже узкое location-only исключение само по себе не даст
qualified acceptance. Полные sites имеют 17 строк, но только 9 входят в COMPLETE
группы; 8 light-controls строк сохраняют group/fingerprint gates.

Следующий этап: решение координатора по location policy и закрытие конкретных
binding/role/companion/fingerprint gates из офлайн-приёмки. Нового control fix
нет; новых запусков, публикации или расходования бюджета этот handoff не разрешает.

Выполнено без push/CI/публикаций/ledger, локальных cargo/rustc/Kani/CBMC и чтения
полных raw logs. Validation — structured replay, integrity checks и пять
in-memory negative checks (REPLAY-CHECKS.json), без independent B1/B2 credit.
