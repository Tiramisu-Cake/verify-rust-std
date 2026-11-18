# W13 — S2 compile repair + cfg-aware contract preflight

Это верификация корректности, не security-работа. Отвечай кратко. Текущая выдача
разрешает исправление; прежнее «approved pins не менять» относится к immutable old
candidate, не запрещает новый. Fresh/current model и owner-enabled /fast сохранить,
без субагентов. STOP только реальный blocker с evidence, не объём/контекст.
Относительные пути от `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Вход: old packageae8f7b2feb739fd51fe72063d4aa71fe36b90790, source
97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a, control
fc058c97335e4a064c7827b8534b3af2f7460bc3, stock0aac unchanged, review0468ccf26c,
GO-request13dc947ad2. Run44264952389 FAILED на compile23.6s,0roots: Kani требует
proof_for_contract для stub_verified(sort8_stable), sorting_s2_batch.rs:155,
general32_weak в sorting+controls+s2_assumed. Identities MATCH/RSS1.35GiB — сведения
координатора; один compact artifact ch8-s2-batch3probes-44264952389-1 допустим при
необходимости уточнить bounded compile receipt. Full/raw logs не нужны.

1. Minimal repair всех affected stub_verified uses, включая positive/negative roots.
   Можно заменить diagnostic summary на explicit kani::stub с именованной заменой
   либо дать matching proof_for_contract registration под тем же effective cfg.
   Самостоятельно выбрать меньшую корректную правку. Explicit stub сохраняет exact
   semantic assumptions/preconditions/frame/old-value/probe relation; пустой/слабый
   stub не подмена сортирующего summary. Неисполненный PFC registration не proof
   qualification. sort13/general32 по-прежнему DIAGNOSTIC_ASSUMED, credit NONE.
2. **Для всех11 manifest roots и их actual effective cfg** составить source-hash-bound
   matrix: активные stub_verified full targets → активные matching PFC harnesses
   в том же compiled crate/cfg. Учесть use aliases/full module paths и cfg/cfg_attr
   all/any/not; wrong-target или PFC только под другим cfg не удовлетворяет gate.
   Нужен узкий parser/checker для реально используемого syntax, не общий Rust parser;
   unsupported/ambiguous cases fail-closed с точным объяснением.
3. Checker исполняется в local package validation и workflow source-preflight после
   checkout pinned std **до build/verification**, а не только в документации.
   Meaningful mutations: missing PFC, inactive/wrong cfg, foreign same-basename
   target/alias, cfg_attr guard; обычный stub не требует PFC; все11 rows проверены.
   Новый checker обязан отвергнуть old97ac для observed class ошибки. Static gate
   не заявляет фактическую успешную Rust/Kani compilation до нового CI.
4. Сохранить3 primary probes/11rows/20required covers/6exact negatives, выражения/
   assumptions/domain/geometry/solver/checks и600s/caps. Пересчитать source locations,
   signatures/hashes/row bindings/request/payload/preflight/shallow после изменения.
   S2-W14-N1 можно явно поправить как неиспользуемые derived6600/1 metadata, без
   изменения runtime limits. Сохранить mandatory service/error/partial controls.

New isolated source/control; old97ac/fc/ae/review immutable. Предпочтителен новый
control sibling над9e14e033f9ee31522b571c127609dcdff76d230b с declared parent;
иначе actual shallow depths пересчитать и проверить. Write g0 только новый
`kani3300/ch8-s2/batch-r1/`: source/control patches+exact pins/trees/request/hashes,
CFG-PFC-MAP.json/md/checker+tests, repair diff map, CI-REQUEST, VALIDATION,HANDOFF.
Не переписывать old batch/review/GO/intake/ledger. Python/static/Git fixtures only;
никаких cargo/rustc/Kani/CBMC/rustfmt/full runner или локального solver опыта.

После READY exact committed delta review14, повтор только GO владельца. Ledger
4076fb01d5de93191f6f012540ee98b2514d36e5: S2 **10/14**, дальнейший учёт решает
владелец; сам не refund/charge/reserve и не предполагай следующий номер. Нет CI/
rerun/cancel/push/publication/ledger. Stage exact own paths, commit --only; не add-A/
reset/rebase. `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Финал `READY <full g0 SHA> <source SHA> <control SHA>` либо реальный STOP.
