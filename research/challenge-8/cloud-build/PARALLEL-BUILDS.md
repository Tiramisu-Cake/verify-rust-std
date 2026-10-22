# Cloud Build: существующий v2 протокол двух slots

Порядок CI evidence для всех версий координатора задаёт [SmallSort Evidence Brief](../EVIDENCE-BRIEF.md): после terminal Build используйте `smallsort-brief BUILD_UUID`; обычные агенты не читают raw logs или archives.

Решение владельца 2026-10-09 13:52 МСК: максимум **два** project-wide
queued/running/unresolved Build; максимум один на стабильного owner и ledger.
Эта документационная редакция сохраняет протокол и число slots. Будущая смена
лимита — отдельная согласованная миграция; бюджеты/сроки/proof scope не изменяются.

`coordination.py`/`control.py` используют общий
`/root/smallsort-ci-coordination/lock` для коротких reconcile/admission/reservation/
submit/accounting transactions, не на время всего Build. `active.json` — v2:
`schema_version: 2`, `max_active: 2`, список `reservations` с owner, phase,
absolute ledger/state, token, item и optional Build ID. Обновления выбирают exact
token и сохраняют peer. Stable proof owners: `select-sort4` и `merge`;
maintainer в своём отдельном разрешённом задании имеет собственную идентичность
(в прочитанном fullmake — `verifast`) и ledger. Все три направления конкурируют
за максимум два occupied slots; owner alias/заимствование чужого ledger запрещены.

Capacity включает reservations и live untracked API Builds, без двойного счёта
по ID/token. Duplicate/inconsistent matches fail closed. Uncertain response
держит один slot своего owner до однозначного match/terminal status либо
окончательного API validation refusal с доказанным отсутствием Build по token.
Не повторять submit при неизвестном ID, не обходить dispatcher/owner alias,
не удалять/сбрасывать active.json и не менять чужие reservations/ledgers вручную.

`request`/`withdraw-request` — advisory, не очередь чередования. Свободный slot
может использовать независимый разрешённый owner; idle peer не блокирует его.
Cancel разрешён только matching owner/phase/ledger/Build; дождаться terminal API.
Короткое client reconciliation чужого счёта — часть протокола, не
разрешение агенту вручную редактировать чужой учёт.

Legacy state читается losslessly; первая mutation атомарно пишет v2. Старые
single-slot clients fail closed на v2. Downgrade требует drain/reconcile и
отдельной reviewed migration. Branch-specific authorized_phase registrations,
recipes и pins нельзя заменять client целиком из другой рабочей ветки.
В этой правке исполняемые clients не переносятся и protocol regression не запускается.

## Свидетельства, без новой приёмки

Историческая подготовительная записка с фразой «validation not run» сохранена
[в архиве](../archive/team-procedure-2026-10-10/README-ARCHIVE.md).
Более поздний merge checkpoint записывает Cloud regression Build
`a0f40e03` на `e918eb875119d912b981da2bfec4e0406e06571e`: 18/18 cases PASS,
100 секунд и наблюдавшийся API overlap двух owners около 115 секунд.
[Датированный результат](https://github.com/Tiramisu-Cake/verify-rust-std/blob/fbc063ce609cc549358e3bbc0f8b3a12b75b3945/research/challenge-8/cloud-build/afternoon-merge-guard/COORDINATION-RESULT.md)
сохраняет точный scope/identities. Это существующее evidence, не новый тест и
не proof acceptance. Synthetic regression использует disposable state, не
production reservations. Новые infra проверки требуют отдельного задания/счёта.
