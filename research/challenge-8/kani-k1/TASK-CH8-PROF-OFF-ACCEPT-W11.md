# TASK — worker11: acceptance PROF-OFF-02 по политике батча (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Политика: [ACCEPTANCE-POLICY-BATCH.md](ACCEPTANCE-POLICY-BATCH.md) (планер, g0 `4e538f840b`) — принята координатором.
Вход: твой intake `kani3300/ch8-profiles/off-ci-batch/run-43784551069/` (control fix `112fcc9ada`), тот же artifact zip.

1. Реализовать политику в классификаторе (отдельной версией, старые receipts не переписывать): unsupported — только
   SUCCESS и связь по exact property ID с assert(false) проверкой недостижимости (подтвердить по 0aac
   `codegen_unimplemented_stmt` file:line); unreachable — по роли (postcondition/frame/relation/обязательный участок →
   блок; защитные ветки — допустимы с перечислением ID/location/причины); неустановленная роль → UNKNOWN.
2. Cover→obligation mapping для каждой positive строки по исходнику harness на source `9fa2f7f977` (какие covers
   свидетельствуют достижение target/wrapper/post-проверок); отсутствие required cover — блок.
3. Full qualified target/contract-wrapper binding (не только terminal identifier) — если можно установить из export
   + source; иначе PENDING явно.
4. Офлайн-переклассификация 62 строк → таблица ACCEPTED / PENDING(причина) / UNKNOWN; consumers после leaf.
   Synthetic tests на новые ветки. Review.
5. g0 `kani3300/ch8-profiles/off-ci-batch/run-43784551069/accept-v2/`: ACCEPTANCE.md, ACCEPT.json, HANDOFF.md.
   Последней строкой `READY <g0>` (+ `<control>` если менялся runner) или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
