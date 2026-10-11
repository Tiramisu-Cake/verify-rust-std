# MERGE selected Drop candidate — ACTIVE / EXPERIMENTAL

2026-10-11: owner разработки receiver/lowering — **merge**. Передача разработки maintainer отменена; исторический запрос сохранён. Новая сессия09:24:22Z–11:24:22Z, finish11:54:22Z; новый бюджет3600Cloudseconds, старые3142retired. Policyc7ca8c467aecf10a4b53039372ee97714f854ee3 прочитана. Scope concrete-u64/x86_64,len1; узкий semantic candidate разрешён, принятие профиля не разрешено. Текущий шаг: merge разработал candidate tool8a3f63ea/profile803abaa5 (v4); fresh Buildfab8b1f5 на65b1679a выполняется в own merge lane. Следующий шаг owner merge: inspect fresh receiver/method/CURRENT/full posts and mandatory controls, сохранить qualification и пакет для maintainer review. Разработка не передана maintainer; профиль NOT_ACCEPTED.

## Предыдущий checkpoint (статусы не повышены)

# MERGE receiver — CLOSED / BLOCKED

Сессия отce2bc9d6, ownmerge/incoming-origin-20261009: start2026-10-11T08:17:34Z,
main09:17:34Z/finish09:47:34Z; закрыта после точного blocker, без новой сессии.
Policyc7ca8c46 прочитана, v2/max2/oneown; peers сохранены.

Fresh846517a9/c8962f4b, frozenprofile0b8cf55b: source/MIR/AST/refinementPASS,
полный physical frame158; первый отказ159:42–44
`Cannot prove ref_origin(gap_guard_addr) = gap_guard_addr.`
Receiver bridge direct-address BLOCKED; actual methodcall/glue/panic NOT_RUN.
Abstract fullborrow можно построить begin_lifetime+borrow, но reborrow result
не связан с actualreceiver. Pointer origin idempotence не передаёт permissions.
Нет новых caller premises/token/semantic patch.

RawFAILURE/INCONCLUSIVE сохранён; exact-message classifier fix + savedreplay4/4
не новая proof-сборка. Fullarchive/inventory/config/source/index/chunks integrity
PASS,12effectivepinsfreshmatch. Helperpositive CURRENT/fullnormalposts/returnleak
и обеbefore/afterfalse controlsfreshPASS; sourcepairs byte-identicalbc08afa0.
Обаmandatorynormal/unwindsmokesfreshPASS; cleanupнашегocallerнеproved.
Guard21/span6 reusedb1da6f8e/7995fccf/profile0b8,NOT_RERUN.

Len1 остаётся QUALIFIED_LEN1_COMPONENT_FRESH_PROOF_PLUS_SAVED_ADMISSION
1396ff47/d491b937; callerFRESH_PASS_BOUNDED_NORMAL_COMPOSITION_FRAGMENT_ONLY.
Domainconcrete-u64/x86_64,len1; профильNOT_ACCEPTED/NOT_FOR_INTEGRATION.
ActualmethodcontrolsNOT_RUN доreceiver bridge. Suppliedvalidtail/heldowner,
thread/type/size/alignment/objectbounds остаются прежними.

CLOSED458/3600Cloudseconds,3142retired/no carryover, ownactive/reservations/
unresolvedNONE/requestWITHDRAWN. Peer active state не менялся.
[Checkpoint](cloud-build/origin-layout/FINAL-CHECKPOINT.md),
[qualification](cloud-build/origin-layout/RECEIVER-QUALIFICATION-20261011.json),
[ledger](cloud-build/origin-layout/BUDGET.json).
Следующий шаг — [локальный запрос владельцу VeriFast](cloud-build/origin-layout/VERIFAST-RECEIVER-REQUEST-20261011.md)
оsource-boundreceiver/dispatchrule; не отправлен внешне. Новой гипотезы/Build нет.
