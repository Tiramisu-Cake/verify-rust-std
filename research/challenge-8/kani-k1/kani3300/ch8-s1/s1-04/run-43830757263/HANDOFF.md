# S1-04 intake — HANDOFF

Одна стадия TASK-CH8-S1-04-INTAKE-W13 завершена.

- Run43830757263, attempt1; control `205b0e98c771a7e6c6b8ec28414494868bcca4e0`;
  std `5be85699b8826e3286c0bf89efb9affefac0acb5`;
  stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Скачаны14/14 artifacts; исходный collect.py собрал35/35 строк, missing_groups=[].
  `collected.json` — неизменённый результат исходного collector, без повышения verdicts.
- Компиляция COMPLETE14/14, proof выполнен35/35:27 SUCCESS,8 assertion FAILURE,0 TIMEOUT.
  По oracle6 EXPECTED,29 UNKNOWN; все4 unions INCOMPLETE_CASES; proof credit NONE.
  Все16 exact-N случаев SUCCESS; исходные4 symbolic harness не запускались.
- Причина красных jobs — acceptance gates/selected_unknown. Fatal runner/compile/source drift нет.
  UNKNOWN:23 exception inventories,3 macro source locations,2 unbound activation oracles,
  1 human-readable cover-message→property-ID mismatch. Per-root RSS UNKNOWN.
- RESULT.md — сводка/таблицы; ROWS.json — exact failures, exceptions, covers и ресурсы;
  GROUPS.json — compile boundary/elapsed, driver exit/wall/group RSS;
  evidence/, PROVENANCE.json, BOUNDED-EXCERPTS.json — сохранённые structured evidence и bounded previews.

Минимальный кандидат `source-binding-fix.patch` меняет только3 locations в request:
добавляет pinned macro declaration line29, сохраняет invocation anchors66/67/68 и source hash.
Patch применим к control205b;15 отрицательных мутаций отвергнуты.
Offline replay исправляет только WRONG_SOURCE_BINDING→INCOMPLETE_CHECK_INVENTORY/UNKNOWN.
Control не менялся, новый control commit не создавался. Candidate review NOT_RUN;
перед будущим submit нужен review и новый request hash. Исходный collected.json не переписывать.

Следующей стадии: отдельно квалифицировать required checks/unreachable/unsupported,
независимо привязать именованные covers/success assertions и false-ensures wrappers.
Не принимать2 activation failures по post-hoc oracle и не заменять bindings количеством SAT.
Отключение gates/controls не является исправлением. Нового CI это поручение не разрешает.

Повтор статической проверки (не запускает verifier):

```sh
python3 intake.py \
  --scratch /root/ch8-s1-04-intake-w13/run-43830757263 \
  --control /root/kani-ch8-s1-04-depth-w13 \
  --std /root/verify-rust-std-ch8-s1-04-w13
```

VALIDATION.json: PASS;35 original parser replays,3 patched binding replays,15 rejected mutations.
GitHub ZIP digest независимо не проверен; artifact metadata — source claim.
g0 — commit, содержащий этот HANDOFF; его SHA указан в итоговой строке READY.
Автор коммита Tiramisu-Cake <igkharin@gmail.com>, сообщение [skip ci].
Push/CI/публикаций/ledger, raw-log чтения и локальных cargo/rustc/Kani/CBMC не было.
