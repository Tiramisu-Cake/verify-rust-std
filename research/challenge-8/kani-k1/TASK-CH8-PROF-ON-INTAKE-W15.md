# TASK — worker15: Profiles ON intake по accept-v4 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: [RESULT.md](kani3300/ch8-profiles/on-ci/run-43798838603/RESULT.md) (g0 d07f0eaa55); artifact id 14198355109,
уже распакован read-only: /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/profon/art (не менять; свои файлы — в g0).
Классификатор — accept-v4 (kani3300/ch8-profiles/off-ci-batch/run-43784551069/accept-v4/) по
ACCEPTANCE-POLICY-BATCH.md, с поправками на ON из твоего RISKS.md / CLASSIFIER-REUSE.json.

1. Применить классификатор ко всем 62 строкам: ACCEPTED / BLOCKED_TOOL (с exact property ID unsupported/
   instrumentation check) / REJECTED / PENDING. Instrumentation-only unreachable (kani::mem_init::*) — отдельной
   категорией с обоснованием по роли, не смешивать с post/frame/relation.
2. Для 13 строк с Kani-конструкциями: подтвердить, что failure — единственный failure и лежит вне кода
   под доказательством; для rejects_always_true — что собственные assertion.4/.6 упали (negative сработал),
   но строка всё равно BLOCKED.
3. Сравнить с OFF построчно (ON-only различия в unreachable/covers).
4. g0 kani3300/ch8-profiles/on-ci/run-43798838603/accept/: ACCEPTANCE.md, ACCEPT.json, HANDOFF.md.
   Коммит [skip ci], author Tiramisu-Cake <igkharin@gmail.com> в команде. Последней строкой READY <g0> или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать (grep bounded).
