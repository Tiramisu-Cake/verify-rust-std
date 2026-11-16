# TASK — PROF-ON-02 intake по accept-v4 (одна стадия на воркера)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: [RESULT.md](kani3300/ch8-profiles/on-ci/fix/run-43808894294/RESULT.md); BINDING-SPEC.json и CLASSIFICATION.md
пакета fix/ (g0 7d1ae3dd04); распакованные artifacts read-only: /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/prof02/on и /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/prof02/off.
Классификатор: accept-v4 (ON-вариант — intake.py из run-43798838603/accept/, OFF — accept-v4 из off-ci-batch).
Политика ACCEPTANCE-POLICY-BATCH.md. Исторические admissions не переносить; новая строка merge4 и consumer
merge len4 — fresh binding к новому leaf той же ветки.

- **worker15 — ON lane** → g0 kani3300/ch8-profiles/on-ci/fix/run-43808894294/accept-on/
- **worker11 — OFF lane** → g0 kani3300/ch8-profiles/on-ci/fix/run-43808894294/accept-off/
  (in-run states SOURCE_STAGE_TARGET_MISMATCH/INCOMPLETE_CHECK_INVENTORY — устаревшие метки runner, как в PROF-OFF-02)

Каждому: все 63 строки ACCEPTED/BLOCKED_TOOL/REJECTED/PENDING с exact binding; построчное сравнение с предыдущим
прогоном своей ветки (ON: run 43798838603 accept; OFF: run 43784551069 accept-v4). ACCEPTANCE.md, ACCEPT.json,
HANDOFF.md. Коммит [skip ci], author Tiramisu-Cake <igkharin@gmail.com>; файлы другого воркера не трогать.
Последней строкой READY <g0> или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать (grep bounded).
