# Acceptance Profiles OFF / P-prime

2026-11-16. Вердикт по политике; без запуска CI и без изменения classifier/receipts.
Основание: [RESULT run 43784551069](kani3300/ch8-profiles/off-ci-batch/run-43784551069/RESULT.md).
Числа ниже — claims этой записки, не повторная независимая проверка batch.

**Согласен отменить безусловные veto на любой `unreachable` и непустой
`unsupported_constructs`. Проект принимаю с уточнениями ниже.**

1. **Positive:** exact harness имеет Kani `SUCCESS`; полный согласованный inventory
   не содержит `FAILURE`, `UNDETERMINED`, `ERROR`, `UNKNOWN`, `other` или неизвестных
   статусов. Отсутствующие/повреждённые поля и потерянные properties дают `UNKNOWN`.
   Сохраняются проверки source/tool/profile/config identities, полного target и
   contract binding, unwind, включённых checks и consumer→accepted-leaf dependencies.
   Group exit и итоговый счётчик не заменяют verdict каждой строки.

2. **Unsupported:** допускаются записи только со статусом `SUCCESS`, связанные
   по exact property ID с проверкой недостижимости unsupported construct в том же
   harness/export. В stock `0aac16ef62da9e9d5645782d458593e5d78143ba`
   `codegen_unimplemented_stmt` генерирует `assert(false)` перед `assume(false)`:
   успех этой проверки означает недостижимость construct в заданной модели.
   Поэтому непустой список сам по себе не blocker; reachable unsupported, failed
   unwinding и undefined-function failures блокируют acceptance. Одной строки
   `status: SUCCESS` без подтверждённого типа/связи property недостаточно.
   См. [семантику unsupported в Kani](https://model-checking.github.io/kani/rust-feature-support.html).

3. **Unreachable:** принадлежность библиотечному helper сама по себе не оправдание;
   важны роль property и заявленный domain. Все исключения перечисляются в receipt:
   ID, location/function, статус, связь с target/wrapper и причина допустимости.
   Недостижимая обязательная postcondition/frame/relation assertion либо участок,
   который обязан исполняться в заявленном сценарии, блокирует acceptance.
   Ожидаемая недостижимая защитная ветка допустима также внутри target/wrapper
   после явного разбора. Нулевой `unreachable` в target/wrapper можно оставить
   консервативным первым gate, но это сильнее необходимого условия корректности.
   Неустановленная принадлежность/роль — `UNKNOWN`, без автоматического helper exemption.
   См. [значение статусов Kani](https://model-checking.github.io/kani/verification-results.html).

4. **Vacuity:** все covers имеют `SATISFIED`; каждый заранее заданный required cover
   присутствует по ID/смыслу в соответствующей строке. Отсутствующий cover
   также блокирует acceptance. Covers должны свидетельствовать достижение actual
   target и требуемых участков wrapper/проверок после relevant assumptions,
   включая предусмотренные нетривиальные случаи. Cover перед вызовом этого не
   устанавливает. SAT — существование исполнения; даже 179/179 не доказывает
   полноту domain, всех ветвей или независимость assumptions. Эти claims требуют
   проверки harness и отображения covers→obligations; счётчик не заменяет её.
   См. [семантику `kani::cover`](https://model-checking.github.io/kani-verifier-blog/2023/01/30/reachability-and-sanity-checking-with-kani-cover.html).

5. **Negatives:** сохраняются 9/9 сбоев на заранее заданных named checks,
   exact binding и отсутствие посторонних failures. `FAILURE` вообще недостаточно;
   oracle нельзя подбирать задним числом. Frame negative с placeholder в manifest
   остаётся `PENDING` до независимого binding, как прямо отмечено в RESULT.

**Для этого batch:** 53/53 `SUCCESS`, 179/179 SAT, 1505 unreachable и 180 successful
unsupported записей совместимы с предлагаемой политикой, но сами не дают 53 accepted.
Нужны разбор unreachable по строкам, cover→obligation mapping и закрытие оставшихся
binding/oracle gates. RESULT оставляет full qualified target/contract-wrapper binding
`PENDING`; terminal identifier его не заменяет. Текущий independent acceptance
остаётся `PENDING`, proof credit `NONE`; исторические verdicts/ledgers не меняются.
