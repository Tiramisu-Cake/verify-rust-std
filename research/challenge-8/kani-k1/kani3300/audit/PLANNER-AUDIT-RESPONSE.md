Отчёт dff05db0c8 прочитан целиком. Моя прежняя оценка готовности части 1 была преждевременной: до исправления P0 часть 1/B1 не подавать; прежний CI не покрывал различающий typed-MU padding случай.
1. Согласие/уточнения по выводам аудита:
   §2.1 P0 — согласен: for_storage даёт all-true extent, который ошибочно используется typed MU transfers. Нужна preserve-mask D(T), для flat arrays — по rustc stride; raw copy остаётся полным extent.
   §2.2 — согласен с OR data ranges обычного union и разницей field-store/whole-create. Preserve никогда не устанавливает true; добавить uninitialized data внутри mask и сохранение wide-tail после narrow store.
   §2.3 — согласен с логикой witness/live source IDs и узким DFCC exception; это не доказательство общей PFC-совместимости. Нужны legal/illegal/clause controls на одном roundtrip.
   §2.4 P0 — согласен: has_body и InstanceKind::Item расходятся; missing pair может попасть в bless fallback. Статический пробел подтверждён, достижимый false SUCCESS ещё не измерен.
   §2.5 P0 — согласен: Err теряет весь current_target, включая ранее собранные ops/entry loads; условный touches_shadow и обход Virtual не дают общего решения. Прежний G1 workaround не считаю достаточным.
   §2.6 P0 — согласен с MIR-разделением. Не согласен с любым blanket reset всех Move и с blanket оправданием всех moved-from чтений; конкретные in-place Call(Move) требуют проверки.
   §3 — согласен с cache reuse до GOTO, но не с объявлением причины FAIL установленной. Fresh prototype — причинный эксперимент, не готовый fix; stale last_writer не заменяет cache identity/структурный MIR.
   §4.1 — согласен; Pat/current_offset и nested-enum local-offset comparison считаю блокирующими для затронутого layout-домена до выпуска. Array reverse/raw_eq требуют отдельных controls либо явного Unsupported.
   ZST backend: согласен сначала проверить чистую базу; abort без G1 пока не установлен. Допустимый fat-pointer value не означает поддержку unsized pointee; guards нужны до ABI/ZST shortcuts.
   §4.2 — согласен с границами CI/fragment goldens/PARTIAL. PASS suite не исключает посторонний failure в negative harness; проверять named property/count/reached read, не только общую строку FAILURE.
   §4.3 — согласен с отдельной частью 1 и последующим B1; PFC OOM раскрывать, не выдавая за установленный upstream OOM/регрессию. Повторная минимизация уже малых repro вторична.
   §5 — N4 replay поддерживаю после native-приёмки нужного пути; расширение к N8/N16 отложить до поддержки соответствующих select/compound операций. Invalid-value и произвольные длины остаются самостоятельными обязательствами.
2. Стадии: два Codex-воркера, одна завершённая стадия на сессию, отдельные клоны/immutable bases; каждая заканчивается review-пакетом и STOP. Fork CI запускает координатор.
   W1-A1: от 1cd96e354 разделить storage extent и typed MU preserve-mask в assignment/StoreArgument/LoadArgument/return; маска сохраняет исходный false, padding destination сбрасывается.
   Контроли A1: физически initialized padding → raw copy сохраняет / typed assignment и bodyful arg/return не гарантируют; data bytes сохраняются; partial data остаётся false; N>1 array проверяет stride/offset.
   W2-B1 параллельно: отдельный base resolver-fix — один super_terminator, сохранение накопленных ops при Err, явная классификация Virtual/non-Item; единый владелец diagnostic, осмысленное обновление legacy golden допустимо.
   Контроли B1: пустой entry с loads, уже накопленные ops, обычный FnPtr, erased/wrapped pointer, virtual/global/escaped cases с delayed seeds и без; source finding не объявлять измеренным false SUCCESS.
   W1-A2: layout patch отдельными коммитами — Pat передаёт current_offset; enum variants сравниваются в локальной системе offsets, затем смещение композиции применяется ровно один раз.
   Контроли A2: nested Pat/enum на ненулевом offset, одинаковые layouts positive и differing-padding Unsupported; array MU→T и raw_eq — подтвердить покрытие либо закрыть непокрытую форму guard.
   W2-B2 параллельно: вернуть десять удалённых cases как диагностический материал; получить pinned MIR через fork CI для Copy, assignment Move, address-taken/in-place Call(Move), forget и reinit.
   Сверить Miri на том же пине, если доступен; иначе не приписывать ему измеренный результат. Наблюдать тот же live object, отличать deinit от dangling/invalid-value.
   W1-A3 после B1/B2: общий caller/callee transfer predicate/протокол; bodyful shim без парного эффекта отклонять. Проверить несколько args, вложенные/повторные calls, signature/size/index и обязательный return0.
   Отсутствие выбранного arg в подтверждённом текущем вызове отделить от отсутствия протокола; непарный return не bless. Не заменять все fallback на true или false.
   Для подтверждённого in-place Move — сначала сохранить/передать witness state, затем deinit source; одних source IDs недостаточно, если shadow уже очищен. До модели — fail-closed только соответствующая достижимая форма.
   W2-B3 параллельно: ZST reduction на чистой базе и candidate, checks off/on; Unsupported/setup error не считать отсутствием abort. [();2], aligned ZST, offset и all-ZST controls обязательны.
   После base repro — отдельный backend-fix; если эффект возникает только через G1 lowering, оставить отдельный зависимый commit B1. Не расширять backend patch до установления причины.
   W1-A4: интегрировать принятые resolver/layout/protocol/Move решения, полный fork CI точного SHA, обновить scope/PR-текст; отдельный upstream layout/resolver patch допустим до части 1.
   Legal PFC + те же frame/clause negatives сохранять; ресурсный limit раскрыть и сузить compatibility claims, не ослабляя checks. Publication gate — P0 закрыты либо неподдержанные формы явно отвергаются.
   W2-B4: отдельный realloc effect/repro — success grow/shrink переносит prefix state min(old,new), новый tail uninit, failure сохраняет старый объект/state; live source identity фиксировать до освобождения.
   Документировать gap недостаточно для молчаливого SUCCESS достижимого неподдержанного эффекта: до модели нужен честный guard/граница. Интегрировать после фиксации нового mem_init ABI, без параллельного редактирования общих call/model handlers.
   W1-A5 после A4: пересобрать G1/B1 от исправленной части 1, перенести выбранный ZST dependency и новый resolver policy; CI-only историю исключить, старый зелёный CI не переносить на новую модель.
   Сохранить OR обычного union отдельно от MU D(T); controls аудитора — false внутри preserve-mask, narrow store сохраняет внешние bytes, whole reset очищает хвост, overlap/arg-return/ZST/rejection/move-policy пары.
   Финал A5: named per-harness outcomes без дополнительных ошибок, full fork CI итогового SHA; PR-B1 ограничен pointee, G2/compound не заявлять закрытыми.
3. T1b pilot полезен сейчас как независимый один эксперимент, но не предикат исправления части 1: сначала fork CI компиляции 94467a244 и актуальный review, затем только решение владельца о новом бюджете.
   Оставить frozen C2/CMP2, library919cc3e2 и те же три roots/flags; не смешивать cache isolation с новыми MU/transfer fixes. Сравнить cache-instance/структурный MIR, actual order и собственные checks writer.
   Три SUCCESS без сохранённых checks не принимаются. Перед production — новая init/uninit пара, matched negatives, multi-root/loop/compound regressions и стоимость компиляции; чистый upstream repro нужен отдельно.
4. Cloud: подготовка всех стадий и native/MIR/backend/regression gates через fork CI координатора требуют Cloud $0; локальные компиляторы/тесты воркеры не запускают. Доступность Miri на пине отдельно подтвердить.
   Единственный предлагаемый Cloud сейчас — T1b pilot: резерв $0.4455, отдельный cap $0.50, одна попытка; старые $0.341 автоматически не переносить. Без решения владельца dispatch нет.
   Поздний verify-std N4 пакет (U8, split written/unwritten scratch controls, calibration pair) — отдельное решение после приёмки соответствующего пути: при 5×3m резерв $0.6075, cap до $0.80.
   При выборе обоих этапов суммарные предложенные caps $1.30, резервы $1.0530; это не уже разрешённый расход. Обязательного дополнительного native GCB при достаточном fork CI не предлагаю.
